from ingestion.ingest_pipeline import run_pipeline

kg = run_pipeline(
    filename="somefile.pdf", # should be defined by user input
    upstage_key="your_upstage_key",
    openai_key="your_openai_key"
)
