import json, pathlib

from services.ocr import analyze_bytes

path = "/home/chief/Projects/anerkennung_ai_cockpit/dummy_docs/degree_HM.pdf"
p = pathlib.Path(path)
b = p.read_bytes()
res = analyze_bytes(b)
print(json.dumps({
    "doc_type": res.doc_type,
    "fields": res.fields,
    "len_text": len(res.text)
}, ensure_ascii=False, indent=2))



