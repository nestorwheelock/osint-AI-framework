# Data Model (initial)

Subject(id, name, aliases[], tags[], created_at)
Session(id, subject_id, status, config_json, started_at, finished_at)
Query(id, subject_id, text, engine, run_at, results_count)
WebPage(id, subject_id, url, canonical_url, final_url, http_status, fetched_at,
        html_blob, screenshot_path, pdf_path, extracted_text, lang, content_hash)
AnalysisRun(id, subject_id, web_page_id?, pipeline_name, model, prompt_version,
            status, cost_tokens, started_at, finished_at, output_json)
Entity(id, subject_id, kind, value, confidence, spans[], source_analysis_run_id, web_page_id)
Label(id, name); WebPageLabel(web_page_id,label_id, user_id)
ExportJob(id, subject_id, format, status, path, created_at)
