import os
import re
import shutil
from typing import List
from ..contracts.types import Article, PublisherConfig
from ..actions.utils import sanitize_content_links, get_safe_path_elements

def generate_dashboard(articles: List[Article], config: PublisherConfig):
    """
    生成首頁 Dashboard
    1. 讀取 KB/pages/index.md (Hero)
    2. 自動更新最新文章清單
    3. 同時寫回 KB/pages/index.md (讓 Logseq 看到)
    4. 寫到 quartz/content/index.md (網頁用)
    """
    index_src = os.path.join(config.logseq_dir, "pages", "index.md")
    
    # Fallback copy
    if not os.path.exists(index_src):
        old_src = os.path.join(config.logseq_dir, "index.md")
        if os.path.exists(old_src):
            shutil.copy(old_src, index_src)

    hero_content = ""
    full_content = ""
    if os.path.exists(index_src):
        with open(index_src, "r", encoding="utf-8") as f:
            full_content = f.read()
            
        marker = "## 🆕 最新發佈"
        if marker in full_content:
            hero_content = full_content.split(marker)[0].strip()
            while hero_content.endswith("---") or hero_content.endswith("\n"):
                if hero_content.endswith("---"):
                    hero_content = hero_content[:-3].strip()
                hero_content = hero_content.strip()
            
            hero_content = re.sub(r'\n\s*-\s*$', '', hero_content).strip()
        else:
            hero_content = full_content
            while hero_content.endswith("---") or hero_content.endswith("\n"):
                if hero_content.endswith("---"):
                    hero_content = hero_content[:-3].strip()
                hero_content = hero_content.strip()
            
            hero_content = re.sub(r'\n\s*-\s*$', '', hero_content).strip()

    # Prepare recent posts
    def get_date_str(art):
        return str(art.date)

    sorted_arts = sorted(articles, key=get_date_str, reverse=True)
    recent_posts = sorted_arts[:10]
    
    logseq_list_lines = ["---", "## 🆕 最新發佈", ""]
    quartz_list_lines = ["---", "## 🆕 最新發佈", ""]
    
    for art in recent_posts:
        date_str = get_date_str(art)
        title = art.title
        categories = art.categories
        
        # Logseq path
        logseq_path = title
        logseq_list_lines.append(f"- {date_str[:10]} - [[{logseq_path}]]")
        
        # Quartz path
        safe_cat, safe_title = get_safe_path_elements(title, categories)
        if safe_cat:
            quartz_path = f"{safe_cat}/{safe_title}"
        else:
            quartz_path = safe_title
        quartz_list_lines.append(f"- {date_str[:10]} - [[{quartz_path}|{title}]]")
        
    logseq_list_lines.append("")
    logseq_list_lines.append(f"> [📅 按日期瀏覽所有文章](/archive)")
    
    quartz_list_lines.append("")
    quartz_list_lines.append(f"> [📅 按日期瀏覽所有文章](/archive)")
    
    logseq_hero = sanitize_content_links(hero_content, for_quartz=False)
    quartz_hero = sanitize_content_links(hero_content, for_quartz=True)
    
    logseq_full = logseq_hero + "\n\n" + "\n".join(logseq_list_lines)
    quartz_full = quartz_hero + "\n\n" + "\n".join(quartz_list_lines)
    
    with open(index_src, "w", encoding="utf-8") as f:
        f.write(logseq_full)
    print(f"  📝 已同步 Logseq 首頁: {index_src}")
    
    target_path = os.path.join(config.quartz_content_dir, "index.md")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(quartz_full)
    print("  🏠 已生成網站首頁: quartz/content/index.md")
