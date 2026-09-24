#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_NAME = 'ziwei_interpretation_claim_registry'
SUPPORTED_SCHEMA_VERSIONS = {'0.1.0-research','0.1.1-research','0.2.0-research','0.2.1-research'}
HARDENED_CONDITIONAL_VERSIONS = {'0.1.1-research','0.2.1-research'}
SOURCE_ROLES = {'PRIMARY_TEXT','SCHOLARLY_SECONDARY','PRACTITIONER_REFERENCE','REFERENCE_IMPLEMENTATION','PROJECT_SYNTHESIS'}
ADMISSION = {'REFERENCE_ONLY','CLAIM_ELIGIBLE','EVALUATION_ONLY','REJECTED'}
LAYERS = {'L4'}
CLAIM_TYPES_BY_VERSION = {
    '0.1.0-research': {'star_core','star_conditional','methodology'},
    '0.1.1-research': {'star_core','star_conditional','methodology'},
    '0.2.0-research': {'star_core','star_conditional','palace_domain','palace_conditional','methodology'},
    '0.2.1-research': {'star_core','star_conditional','palace_domain','palace_conditional','methodology'},
}
ASSERTION_CLASSES = {'historical_core','historical_conditional','named_tradition','practitioner_heuristic','case_inference','project_adoption'}
CONFIDENCE = {'supported','qualified','provisional','conflicted','unsupported'}
SUPPORT = {'single_source_supported','multi_source_supported','tradition_bounded','qualified','conflicted','historical_only','architecture_only','unsupported'}
CLAIM_ADOPTION = {'RESEARCH_CLAIM_ELIGIBLE','REFERENCE_ONLY','REJECTED'}

def err(errors:list[dict[str,str]], code:str, path:str, message:str)->None:
    errors.append({'code':code,'path':path,'message':message})

def nonempty_str(v:Any)->bool:
    return isinstance(v,str) and bool(v.strip())

def str_array(v:Any)->bool:
    return isinstance(v,list) and all(nonempty_str(x) for x in v)

def validate(data:Any)->list[dict[str,str]]:
    errors=[]
    if not isinstance(data,dict):
        err(errors,'ROOT_OBJECT_REQUIRED','$','registry must be object'); return errors
    required=['schema_name','schema_version','record_status','record_kind','record_id','production_routable','interpretation_profile','sources','claims','conflict_groups','privacy','research_result']
    for key in required:
        if key not in data: err(errors,'REQUIRED_FIELD_MISSING',f'$.{key}','required field missing')
    if data.get('schema_name')!=SCHEMA_NAME: err(errors,'SCHEMA_NAME_INVALID','$.schema_name',f'must equal {SCHEMA_NAME}')
    schema_version=data.get('schema_version')
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS: err(errors,'SCHEMA_VERSION_INVALID','$.schema_version',f'must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}')
    claim_types=CLAIM_TYPES_BY_VERSION.get(schema_version,set())
    if data.get('record_status')!='REFERENCE-ONLY': err(errors,'RECORD_STATUS_INVALID','$.record_status','must be REFERENCE-ONLY')
    if data.get('record_kind')!='ziwei_interpretation_claim_family_registry': err(errors,'RECORD_KIND_INVALID','$.record_kind','invalid record kind')
    if data.get('production_routable') is not False: err(errors,'PRODUCTION_ROUTABLE_FORBIDDEN','$.production_routable','must be false')
    privacy=data.get('privacy')
    if not isinstance(privacy,dict) or privacy.get('contains_real_birth_data') is not False: err(errors,'PRIVACY_FALSE_REQUIRED','$.privacy.contains_real_birth_data','must be false')
    rr=data.get('research_result')
    if not isinstance(rr,dict): err(errors,'RESEARCH_RESULT_REQUIRED','$.research_result','must be object')
    else:
        if rr.get('production_authority_granted') is not False: err(errors,'PRODUCTION_AUTHORITY_FORBIDDEN','$.research_result.production_authority_granted','must be false')
        if rr.get('scientific_predictive_validity_claimed') is not False: err(errors,'SCIENTIFIC_VALIDITY_FORBIDDEN','$.research_result.scientific_predictive_validity_claimed','must be false')

    sources=data.get('sources')
    if not isinstance(sources,list) or not sources: err(errors,'SOURCES_REQUIRED','$.sources','non-empty array required'); sources=[]
    source_by_id={}
    for i,s in enumerate(sources):
        p=f'$.sources[{i}]'
        if not isinstance(s,dict): err(errors,'SOURCE_OBJECT_REQUIRED',p,'must be object'); continue
        sid=s.get('source_id')
        if not nonempty_str(sid): err(errors,'SOURCE_ID_REQUIRED',p+'.source_id','required'); continue
        if sid in source_by_id: err(errors,'SOURCE_ID_DUPLICATE',p+'.source_id','must be unique')
        source_by_id[sid]=s
        if s.get('source_role') not in SOURCE_ROLES: err(errors,'SOURCE_ROLE_INVALID',p+'.source_role','unsupported source role')
        ads=s.get('admission_status')
        if not str_array(ads): err(errors,'ADMISSION_STATUS_REQUIRED',p+'.admission_status','string array required')
        else:
            for a in ads:
                if a not in ADMISSION: err(errors,'ADMISSION_STATUS_INVALID',p+'.admission_status',f'unsupported {a}')
        if not str_array(s.get('storage_mode')): err(errors,'STORAGE_MODE_REQUIRED',p+'.storage_mode','string array required')
        if not nonempty_str(s.get('independence_status')): err(errors,'INDEPENDENCE_REQUIRED',p+'.independence_status','required')
        if not nonempty_str(s.get('locator')): err(errors,'SOURCE_LOCATOR_REQUIRED',p+'.locator','required')

    claims=data.get('claims')
    if not isinstance(claims,list) or not claims: err(errors,'CLAIMS_REQUIRED','$.claims','non-empty array required'); claims=[]
    claim_ids=set()
    for i,c in enumerate(claims):
        p=f'$.claims[{i}]'
        if not isinstance(c,dict): err(errors,'CLAIM_OBJECT_REQUIRED',p,'must be object'); continue
        cid=c.get('claim_id')
        if not nonempty_str(cid): err(errors,'CLAIM_ID_REQUIRED',p+'.claim_id','required')
        elif cid in claim_ids: err(errors,'CLAIM_ID_DUPLICATE',p+'.claim_id','must be unique')
        else: claim_ids.add(cid)
        if c.get('layer') not in LAYERS: err(errors,'LAYER_INVALID',p+'.layer','must be L4')
        if c.get('claim_type') not in claim_types: err(errors,'CLAIM_TYPE_INVALID',p+'.claim_type',f'unsupported for schema {schema_version}')
        if c.get('assertion_class') not in ASSERTION_CLASSES: err(errors,'ASSERTION_CLASS_INVALID',p+'.assertion_class','unsupported')
        if not nonempty_str(c.get('subject')): err(errors,'SUBJECT_REQUIRED',p+'.subject','required')
        if not nonempty_str(c.get('normalized_statement')): err(errors,'STATEMENT_REQUIRED',p+'.normalized_statement','required')
        refs=c.get('source_refs')
        if not str_array(refs): err(errors,'SOURCE_REFS_REQUIRED',p+'.source_refs','non-empty string array required'); refs=[]
        if refs==[]: err(errors,'SOURCE_REFS_NONEMPTY',p+'.source_refs','must not be empty')
        for ref in refs:
            s=source_by_id.get(ref)
            if s is None: err(errors,'SOURCE_REF_UNRESOLVED',p+'.source_refs',f'unknown source {ref}')
            elif 'CLAIM_ELIGIBLE' not in s.get('admission_status',[]): err(errors,'SOURCE_NOT_CLAIM_ELIGIBLE',p+'.source_refs',f'{ref} is not CLAIM_ELIGIBLE')
        locs=c.get('source_locators')
        if not str_array(locs) or not locs: err(errors,'SOURCE_LOCATORS_REQUIRED',p+'.source_locators','non-empty locator array required')
        app=c.get('applicability')
        if not isinstance(app,dict):
            err(errors,'APPLICABILITY_REQUIRED',p+'.applicability','object required')
        else:
            conditional=c.get('claim_type') in {'star_conditional','palace_conditional'}
            meta=app.get('conditional_activation')
            if conditional and schema_version in HARDENED_CONDITIONAL_VERSIONS and not isinstance(meta,dict):
                err(errors,'CONDITIONAL_ACTIVATION_REQUIRED',p+'.applicability.conditional_activation','required for hardened conditional schema')
            if meta is not None:
                if not conditional:
                    err(errors,'CONDITIONAL_ACTIVATION_FORBIDDEN',p+'.applicability.conditional_activation','only conditional claim types may declare activation')
                elif not isinstance(meta,dict):
                    err(errors,'CONDITIONAL_ACTIVATION_OBJECT_REQUIRED',p+'.applicability.conditional_activation','must be object')
                else:
                    mode=meta.get('mode')
                    if mode not in {'context_only','fact_gated'}:
                        err(errors,'CONDITIONAL_ACTIVATION_MODE_INVALID',p+'.applicability.conditional_activation.mode','must be context_only or fact_gated')
                    for key in ('availability_requires','satisfies_all','satisfies_any','forbids'):
                        if not str_array(meta.get(key)):
                            err(errors,'CONDITIONAL_ACTIVATION_ARRAY_REQUIRED',p+f'.applicability.conditional_activation.{key}','string array required')
                    if mode=='fact_gated' and not meta.get('availability_requires'):
                        err(errors,'CONDITIONAL_AVAILABILITY_REQUIRED',p+'.applicability.conditional_activation.availability_requires','fact_gated mode requires at least one availability fact')
                    if mode=='context_only':
                        for key in ('availability_requires','satisfies_all','satisfies_any','forbids'):
                            if meta.get(key):
                                err(errors,'CONTEXT_ONLY_ACTIVATION_MUST_BE_EMPTY',p+f'.applicability.conditional_activation.{key}','context_only mode must not declare chart predicates')
        if c.get('confidence_status') not in CONFIDENCE: err(errors,'CONFIDENCE_INVALID',p+'.confidence_status','unsupported')
        if c.get('support_status') not in SUPPORT: err(errors,'SUPPORT_INVALID',p+'.support_status','unsupported')
        if not isinstance(c.get('conflict_group_ids'),list): err(errors,'CONFLICT_IDS_REQUIRED',p+'.conflict_group_ids','array required')
        if c.get('adoption_state') not in CLAIM_ADOPTION: err(errors,'CLAIM_ADOPTION_INVALID',p+'.adoption_state','unsupported')

    conflicts=data.get('conflict_groups')
    if not isinstance(conflicts,list): err(errors,'CONFLICT_GROUPS_REQUIRED','$.conflict_groups','array required'); conflicts=[]
    conflict_ids=set()
    for i,g in enumerate(conflicts):
        p=f'$.conflict_groups[{i}]'
        if not isinstance(g,dict): err(errors,'CONFLICT_OBJECT_REQUIRED',p,'must be object'); continue
        gid=g.get('conflict_group_id')
        if not nonempty_str(gid): err(errors,'CONFLICT_ID_REQUIRED',p+'.conflict_group_id','required'); continue
        if gid in conflict_ids: err(errors,'CONFLICT_ID_DUPLICATE',p+'.conflict_group_id','must be unique')
        conflict_ids.add(gid)
        allowed_resolutions={'PRESERVE_CONFLICT','RESOLVED_BY_PROFILE'}
        if schema_version in {'0.2.0-research','0.2.1-research'}: allowed_resolutions.add('PRESERVE_SCOPE_DIFFERENCE')
        if g.get('resolution_status') not in allowed_resolutions: err(errors,'CONFLICT_RESOLUTION_INVALID',p+'.resolution_status',f'unsupported for schema {schema_version}')
        refs=g.get('claim_refs')
        if not isinstance(refs,list): err(errors,'CONFLICT_CLAIM_REFS_REQUIRED',p+'.claim_refs','array required'); refs=[]
        for ref in refs:
            if ref not in claim_ids: err(errors,'CONFLICT_CLAIM_REF_UNRESOLVED',p+'.claim_refs',f'unknown claim {ref}')

    for i,c in enumerate(claims):
        for gid in c.get('conflict_group_ids',[]) if isinstance(c,dict) else []:
            if gid not in conflict_ids: err(errors,'CLAIM_CONFLICT_REF_UNRESOLVED',f'$.claims[{i}].conflict_group_ids',f'unknown conflict {gid}')
    return errors

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('registry',type=Path)
    args=ap.parse_args()
    data=json.loads(args.registry.read_text(encoding='utf-8'))
    errors=validate(data)
    if errors:
        print(json.dumps({'status':'FAIL','errors':errors},ensure_ascii=False,indent=2)); return 1
    print(json.dumps({'status':'PASS','registry':str(args.registry),'claims':len(data['claims'])},ensure_ascii=False)); return 0

if __name__=='__main__': raise SystemExit(main())