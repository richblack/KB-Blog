from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Article:
    title: str
    source_file: str
    body: str
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    type: str = "block"  # 'block' or 'file'
    
    # Target path info
    target_dir: str = ""
    filename: str = ""
    
    # Enriched metadata
    slug: str = ""
    date: str = ""
    tags: List[str] = field(default_factory=list)
    categories: str = "Uncategorized"

@dataclass
class PublisherConfig:
    logseq_dir: str = "./KB"
    quartz_content_dir: str = "./quartz/content"
    publish_uuid: str = "dc0b4d96-f96f-4c1b-9d35-e1a5de79d979"
    max_asset_size_mb: int = 25
