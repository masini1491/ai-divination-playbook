from pathlib import Path
import argparse, hashlib, itertools, json, math, tempfile, urllib.request, zipfile
import cv2, mediapipe as mp, numpy as np

MODEL_URL="https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_SHA="fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
MP_VER="1.0.1"
ZIP_DEFAULT=Path(r"C:\Users\user\Documents\X\MOHI_sample_10p_3s_5i.zip")
OUT_DEFAULT=Path(r"C:\Users\user\Documents\X\MOHI_repeatability_results.json")

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def model(path):
    if not path.exists(): urllib.request.urlretrieve(MODEL_URL,path)
    got=sha(path)
    if got!=MODEL_SHA: raise RuntimeError(f"model SHA mismatch: {got}")
    return got

def resize(img):
    h,w=img.shape[:2]; m=max(h,w)
    if m<=1600: return img,1.,1.
    q=1600/m; nw,nh=round(w*q),round(h*q)
    out=cv2.resize(img,(nw,nh),interpolation=cv2.INTER_AREA)
    return out,nw/w,nh/h

def cname(c):
    return getattr(c,"category_name",None) or getattr(c,"display_name",None)

def detect(lm,img,rw,rh,sx,sy):
    rgb=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB) if img.ndim==2 else cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    r=lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(rgb)))
    wh,ww=img.shape[:2]; out=[]
    for i,L in enumerate(r.hand_landmarks):
        hand=[]
        for j,p in enumerate(L):
            x=float(p.x)*ww/sx; y=float(p.y)*wh/sy
            hand.append([x,y,x/rw,y/rh,float(p.z)])
        hd=None; sc=None
        if i<len(r.handedness) and r.handedness[i]:
            hd=cname(r.handedness[i][0]); sc=float(r.handedness[i][0].score)
        out.append({"handedness":hd,"score":sc,"lm":hand})
    return out

def basis(hand):
    L=hand["lm"]; p0=np.array(L[0][:2]); p5=np.array(L[5][:2]); p17=np.array(L[17][:2])
    m=(p5+p17)/2; eyv=m-p0; H=float(np.linalg.norm(eyv)); W=float(np.linalg.norm(p5-p17))
    if H<=1e-9 or W<=1e-9: raise RuntimeError("degenerate basis")
    ey=eyv/H; a=np.array([ey[1],-ey[0]]); b=-a; ex=a if np.dot(a,p5-m)>=np.dot(b,p5-m) else b
    can=[]
    for p in L:
        v=np.array(p[:2])-p0
        can.append([float(np.dot(v,ex)/W),float(np.dot(v,ey)/H)])
    return {"w":W,"h":H,"ang":math.degrees(math.atan2(ey[1],ey[0])),"can":can}

def ad(a,b): return abs((b-a+180)%360-180)

def pair(a,b):
    A=a["hand"]["lm"]; B=b["hand"]["lm"]
    anc=[np.linalg.norm(np.array(A[i][2:4])-np.array(B[i][2:4])) for i in (0,5,17)]
    ca=np.array(a["basis"]["can"]); cb=np.array(b["basis"]["can"]); cd=np.linalg.norm(ca-cb,axis=1)
    wa,wb=a["basis"]["w"],b["basis"]["w"]; ha,hb=a["basis"]["h"],b["basis"]["h"]
    return {"anchor_mean":float(np.mean(anc)),"anchor_max":float(np.max(anc)),"angle_deg":ad(a["basis"]["ang"],b["basis"]["ang"]),"width_rel":abs(wa-wb)/((wa+wb)/2),"height_rel":abs(ha-hb)/((ha+hb)/2),"canonical_mean":float(np.mean(cd)),"canonical_max":float(np.max(cd))}

def summ(vals):
    if not vals:return None
    x=np.array(vals,float)
    return {"n":len(vals),"mean":float(x.mean()),"median":float(np.median(x)),"p90":float(np.percentile(x,90)),"p95":float(np.percentile(x,95)),"min":float(x.min()),"max":float(x.max()),"std":float(x.std())}

def psum(P):
    keys=("anchor_mean","anchor_max","angle_deg","width_rel","height_rel","canonical_mean","canonical_max")
    return {"pairs":len(P),**{k:summ([x["m"][k] for x in P]) for k in keys}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("zip",nargs="?",default=str(ZIP_DEFAULT)); ap.add_argument("--output",default=str(OUT_DEFAULT)); a=ap.parse_args()
    zp=Path(a.zip); op=Path(a.output)
    if getattr(mp,"__version__","")!=MP_VER: raise RuntimeError(f"Need mediapipe=={MP_VER}")
    mdl=zp.parent/"hand_landmarker.task"; msha=model(mdl)
    with zipfile.ZipFile(zp) as z:
        if "manifest.tsv" not in z.namelist(): raise RuntimeError("manifest.tsv missing")
        rows=[]; lines=z.read("manifest.tsv").decode().splitlines(); hdr=lines[0].split("\t"); ix={k:hdr.index(k) for k in ("sample_path","dataset_person_id","session","image_index")}
        for line in lines[1:]:
            c=line.split("\t"); rows.append({"file":c[ix["sample_path"]],"p":int(c[ix["dataset_person_id"]]),"s":int(c[ix["session"]]),"i":int(c[ix["image_index"]])})
        persons=sorted({r["p"] for r in rows})
        if len(rows)!=150 or len(persons)!=10: raise RuntimeError(f"unexpected manifest rows/persons: {len(rows)}/{len(persons)}")
    opt=mp.tasks.vision.HandLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(mdl)),running_mode=mp.tasks.vision.RunningMode.IMAGE,num_hands=2,min_hand_detection_confidence=.5,min_hand_presence_confidence=.5,min_tracking_confidence=.5)
    out={"status":"REFERENCE-ONLY / MOHI PINNED REPEATABILITY","zip_sha256":sha(zp),"model_sha256":msha,"mediapipe":MP_VER,"images":[]}; usable=[]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        with zipfile.ZipFile(zp) as z: z.extractall(td)
        with mp.tasks.vision.HandLandmarker.create_from_options(opt) as lm:
            for n,r in enumerate(rows,1):
                img=cv2.imread(str(td/r["file"]),cv2.IMREAD_UNCHANGED); rec={**r}
                if img is None: rec.update({"decode":False,"candidates":None,"usable":False}); out["images"].append(rec); continue
                rh,rw=img.shape[:2]; work,sx,sy=resize(img); hands=detect(lm,work,rw,rh,sx,sy); rec.update({"decode":True,"raw":[rh,rw],"work":list(work.shape[:2]),"candidates":len(hands),"usable":len(hands)==1})
                if len(hands)==1: rec["hand"]=hands[0]; rec["basis"]=basis(hands[0]); usable.append(rec)
                out["images"].append(rec); print(f"[{n:03d}/150] P{r['p']:03d} S{r['s']} I{r['i']}: {len(hands)}")
    dist={}
    for r in out["images"]:
        k="decode_failed" if r["candidates"] is None else str(r["candidates"]); dist[k]=dist.get(k,0)+1
    out["detector"]={"total":150,"usable":len(usable),"usable_rate":len(usable)/150,"candidate_distribution":dist}
    by={}
    for r in usable: by.setdefault((r["p"],r["s"]),[]).append(r)
    within=[]; cross=[]; per={}
    for p in persons:
        pp={"within":{},"cross":{}}
        for s in (1,2,3):
            R=by.get((p,s),[]); P=[{"p":p,"a":[x["s"],x["i"]],"b":[y["s"],y["i"]],"m":pair(x,y)} for x,y in itertools.combinations(R,2)]; within+=P; pp["within"][str(s)]=psum(P)
        for a1,b1 in ((1,2),(2,3),(1,3)):
            A=by.get((p,a1),[]); B=by.get((p,b1),[]); P=[{"p":p,"a":[x["s"],x["i"]],"b":[y["s"],y["i"]],"m":pair(x,y)} for x in A for y in B]; cross+=P; pp["cross"][f"{a1}-{b1}"]=psum(P)
        per[str(p)]=pp
    out["repeatability"]={"within":psum(within),"cross":psum(cross),"per_person":per}
    op.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\nDONE"); print(json.dumps(out["detector"],indent=2)); print(op)

if __name__=="__main__": main()
