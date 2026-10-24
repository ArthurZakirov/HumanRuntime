import argparse, json, subprocess, re, time, sys
from pathlib import Path
DS="c27c8188-cf57-402b-8dc8-1b3b6c7cd23a"
REWE_URL_BASE="https://www.rewe.de/shop/products/"
CAT=Path.home()/".local/share/humanruntime/rewe-products.json"

def ntn(*args, data=None):
    cmd=["ntn","api",*args]
    if data is not None:
        cmd+=["-d","@-"]
    for trial in range(5):
        p=subprocess.run(cmd,input=json.dumps(data,ensure_ascii=False) if data is not None else None,capture_output=True,text=True,timeout=55)
        if p.returncode==0:
            try:return json.loads(p.stdout)
            except:raise RuntimeError("Not JSON:"+p.stdout[:300])
        if any(s in (p.stderr+p.stdout).lower() for s in ("rate limit","429","temporarily","timeout")):
            time.sleep(1+trial*2)
            continue
        raise RuntimeError(f"ntn failure: {p.stderr[-650:]} {p.stdout[-350:]}")
    raise RuntimeError("API retries exhausted")

def prop_text(prop):
    v=prop or {}
    return "".join(i.get("plain_text","") for i in v.get("rich_text",[]) or v.get("title",[]))

def rt(value):
    return {"rich_text":[{"type":"text","text":{"content":str(value)}}]} if value else {"rich_text":[]}

def price(s):
    m=re.search(r"(\d+(?:\.\d{3})*,\d{2})\s*€",s or "")
    return float(m.group(1).replace(".","").replace(",",".")) if m else None

def clean(t):
    return re.sub(r"^[\W_]+","",t).strip()

def properties(row,sources):
    title=clean(row["title"])
    return {"Produkt":{"title":[{"type":"text","text":{"content":title}}]},
            "Artikel-ID":rt(row["id"]),
            "Produktlink":{"url":REWE_URL_BASE+row["id"]},
            "Preis zuletzt (EUR)":{"number":price(row.get("price_text"))},
            "Verfügbarkeit":{"select":{"name":"Nicht verfügbar" if row["unavailable"] else "Verfügbar"}},
            "Quelle":{"multi_select":[{"name":s} for s in sources]}}

def verify_rewe_sync(pages,expected_ids):
    # Other merchants coexist in the same Notion catalogue; this sync owns only REWE IDs.
    rewe_pages=[p for p in pages if (p["properties"].get("Produktlink") or {}).get("url","").startswith(REWE_URL_BASE)]
    ids=[prop_text(p["properties"].get("Artikel-ID")) for p in rewe_pages]
    invalid=[
        p["id"] for p in rewe_pages
        if p.get("icon") is not None
        or clean(prop_text(p["properties"]["Produkt"])) != prop_text(p["properties"]["Produkt"])
    ]
    return {
        "total_rows":len(pages),
        "rewe_rows":len(rewe_pages),
        "unique_rewe_ids":len(set(ids)),
        "missing_ids":set(expected_ids)-set(ids),
        "duplicate_ids":{id for id in ids if ids.count(id)>1},
        "invalid_pages":invalid,
    }

def main():
    ap=argparse.ArgumentParser(description="Idempotent REWE catalogue sync into Notion, preserving user-maintained columns.")
    ap.add_argument("--catalogue",type=Path,default=CAT)
    ap.add_argument("--apply",action="store_true",help="Write Notion updates. Without it: preview only.")
    args=ap.parse_args()
    d=json.loads(args.catalogue.read_text())
    for name in ("favorites","purchased"):
        if not isinstance(d.get(name),list) or not d[name]:
            raise ValueError(f"Incomplete/empty REWE {name} listing")
        if len(d[name])!=d.get(name+"_expected"):
            raise ValueError(f"Count mismatch in REWE {name} listing")
    catalog={}
    for group,name in [("purchased","Bereits gekauft"),("favorites","Favoriten")]:
        for row in d[group]:
            id=row["id"]
            if id not in catalog:catalog[id]={"row":row,"sources":set()}
            catalog[id]["sources"].add(name)
    print("SOURCE",len(catalog),"unique products",flush=True)
    if len(catalog)!=len(set(p["id"] for p in d["favorites"]+d["purchased"])): raise ValueError("Product ID reconciliation failed")
    existing={}
    cursor=None
    while True:
        body={"page_size":100}
        if cursor:body["start_cursor"]=cursor
        out=ntn("v1/data_sources/"+DS+"/query",data=body)
        for row in out["results"]:
            id=prop_text(row["properties"].get("Artikel-ID"))
            if (row["properties"].get("Produktlink") or {}).get("url","").startswith(REWE_URL_BASE):
                if not id:raise RuntimeError("REWE product without Artikel-ID")
                if id in existing:raise RuntimeError(f"Duplicate existing Artikel-ID {id}")
                existing[id]=row
        cursor=out.get("next_cursor")
        if not out.get("has_more"):break
    print("EXISTING",len(existing),flush=True)
    created=updated=errors=unchanged=0
    for i,(id,meta) in enumerate(sorted(catalog.items(),key=lambda p:int(p[0])),1):
        attrs=properties(meta["row"],sorted(meta["sources"]))
        old=existing.get(id)
        try:
            if old:
                current=old["properties"]
                comparable={
                    "Produkt":prop_text(current.get("Produkt")),
                    "Artikel-ID":prop_text(current.get("Artikel-ID")),
                    "Produktlink":(current.get("Produktlink") or {}).get("url"),
                    "Preis zuletzt (EUR)":(current.get("Preis zuletzt (EUR)") or {}).get("number"),
                    "Verfügbarkeit":((current.get("Verfügbarkeit") or {}).get("select") or {}).get("name"),
                    "Quelle":sorted(x["name"] for x in (current.get("Quelle") or {}).get("multi_select",[])),
                }
                expected={
                    "Produkt":clean(meta["row"]["title"]),"Artikel-ID":id,
                    "Produktlink":REWE_URL_BASE+id,
                    "Preis zuletzt (EUR)":price(meta["row"].get("price_text")),
                    "Verfügbarkeit":"Nicht verfügbar" if meta["row"]["unavailable"] else "Verfügbar",
                    "Quelle":sorted(meta["sources"]),
                }
                if comparable==expected and old.get("icon") is None:
                    unchanged+=1
                    continue
                if args.apply:
                    ntn("v1/pages/"+old["id"],"-X","PATCH",data={"properties":attrs,"icon":None})
                else:
                    print("WOULD UPDATE",id,meta["row"]["title"],flush=True)
                updated+=1
            else:
                if args.apply:
                    ntn("v1/pages",data={"parent":{"type":"data_source_id","data_source_id":DS},"properties":attrs})
                else:
                    print("WOULD CREATE",id,meta["row"]["title"],flush=True)
                created+=1
            if (created+updated)%20==0:print("PROGRESS",created+updated,"/",len(catalog),flush=True)
        except Exception as e:
            errors+=1
            print("ERROR",id,str(e)[:350],flush=True)
    print("FINISHED created",created,"updated",updated,"unchanged",unchanged,"errors",errors,flush=True)
    if not args.apply:
        print("DRY-RUN: no changes made; use --apply to write",flush=True)
        return
    if errors:sys.exit(1)
    check=[]
    cursor=None
    while True:
        body={"page_size":100}
        if cursor:body["start_cursor"]=cursor
        out=ntn("v1/data_sources/"+DS+"/query",data=body)
        check.extend(out["results"])
        cursor=out.get("next_cursor")
        if not out.get("has_more"):break
    verification=verify_rewe_sync(check,set(catalog))
    print("VERIFY rows",verification["total_rows"],"rewe",verification["rewe_rows"],"unique",verification["unique_rewe_ids"],"expected",len(catalog),"missing",len(verification["missing_ids"]),"duplicates",len(verification["duplicate_ids"]),"invalid_titles_or_icons",len(verification["invalid_pages"]),flush=True)
    if verification["missing_ids"] or verification["duplicate_ids"] or verification["invalid_pages"]:sys.exit(2)

if __name__=="__main__":main()
