import re
import yaml
from pathlib import Path
from typing import List, Optional
from ..contracts.types import Article, PublisherConfig
from .utils import sanitize_content_links

def parse_logseq_file(filepath: Path, config: PublisherConfig) -> List[Article]:
    """
    解析 Logseq 檔案。
    模式 1: Block-Based Article (包含 UUID)
    模式 2: Legacy File Page (標準 Markdown)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️ 無法讀取 {filepath}: {e}")
        return []

    # 忽略 index.md (它是首頁來源，不是文章)
    if filepath.name == "index.md":
        return []

    articles = []
    
    # 模式 1: 尋找包含 UUID 的 Block (優先)
    if config.publish_uuid in content:
        articles.extend(_parse_block_based(filepath, content, config.publish_uuid))
            
    # 模式 2: Legacy File Page (標準 Markdown 前言)
    # 條件: 在 Pages 目錄 + 有 frontmatter + 無 UUID (或 UUID 不在標題，這裡簡化邏輯：如果在 pages 目錄且有 frontmatter)
    # 為了避免重複，如果已經用 Block 模式抓到了，理論上不應該再抓，但為了保險起見，可以檢查 articles 是否為空
    if not articles and "pages" in str(filepath) and content.startswith("---"):
        article = _parse_legacy_file(filepath, content)
        if article:
            articles.append(article)

    return articles

def _parse_block_based(filepath: Path, content: str, publish_uuid: str) -> List[Article]:
    articles = []
    lines = content.split('\n')
    i = 0
    in_code_block = False
    
    while i < len(lines):
        line = lines[i]
        
        # 偵測 Code Block
        if "```" in line:
            in_code_block = not in_code_block
        
        has_valid_uuid = False
        if publish_uuid in line:
            # 移除 inline code 避免誤判
            line_no_code = re.sub(r'(`+).*?\1', '', line)
            if publish_uuid in line_no_code:
                has_valid_uuid = True

        # 尋找包含 UUID 的行 (Title Block)
        if has_valid_uuid and not in_code_block and not line.strip().startswith("id::"):
            # 計算縮排級別
            indent = len(line) - len(line.lstrip())
            
            # 提取標題
            raw_title = line.strip().lstrip('- ').lstrip('# ').replace(f"(({publish_uuid}))", "").strip()
            
            block_content = []
            frontmatter_raw = {}
            
            # 追蹤 Code Block Fence 的縮排
            fence_indent_len = 0
            
            # 往子 Block 掃描
            j = i + 1
            while j < len(lines):
                sub_line = lines[j]
                
                # Global End Marker
                if "🏁" in sub_line:
                    j = len(lines) # Force Finish
                    break
                    
                if not sub_line.strip():
                    j += 1
                    continue
                    
                # Pre-filter System Properties
                clean_check = sub_line.strip()
                if "::" in clean_check:
                        if re.match(r'^(collapsed|id|logseq\.[a-z]+)::\s', clean_check):
                            j += 1
                            continue

                # 偵測子內容中的 Code Block 開關
                is_opening_fence = False
                is_closing_fence = False
                
                if "```" in sub_line:
                    # Normalize fence lang
                    sub_line = re.sub(r'```([a-zA-Z0-9_\-\+]+)', lambda m: '```' + m.group(1).lower(), sub_line)
                    
                    clean_fence_check = sub_line.replace('\t', '').strip()
                    if clean_fence_check.startswith("- "): 
                            clean_fence_check = clean_fence_check[2:].strip()
                    
                    if not in_code_block:
                        in_code_block = True
                        fence_indent_len = len(sub_line) - len(sub_line.lstrip())
                        is_opening_fence = True
                    else:
                        if clean_fence_check == "```" or clean_fence_check.startswith("```"):
                            in_code_block = False
                            is_closing_fence = True
                
                sub_indent = len(sub_line) - len(sub_line.lstrip())
                
                # 如果縮排回到父層級或更少，表示此 Block 結束
                if sub_indent <= indent and not in_code_block and not is_closing_fence:
                    break

                # Frontmatter Block Detection
                clean_sub_check = sub_line.strip()
                if not in_code_block and clean_sub_check.lower().startswith("- frontmatter"):
                    fm_indent = sub_indent
                    k = j + 1
                    while k < len(lines):
                        fm_line = lines[k]
                        if not fm_line.strip():
                            k += 1
                            continue
                        fm_sub_indent = len(fm_line) - len(fm_line.lstrip())
                        if fm_sub_indent <= fm_indent:
                            break
                        fm_text = fm_line.strip().lstrip("- ")
                        fm_text = fm_text.lstrip("- ") 
                        if ":" in fm_text:
                            key, value = fm_text.split(":", 1)
                            frontmatter_raw[key.strip()] = value.strip()
                        k += 1
                    j = k 
                    continue
                    
                # 計算相對層級 (Tabs)
                raw_indent = sub_line[:sub_indent]
                relative_tabs = raw_indent[indent:].count('\t')
                if relative_tabs == 0 and sub_indent > indent:
                    relative_tabs = (sub_indent - indent) // 2
                
                content_part = sub_line[sub_indent:]
                
                if in_code_block or is_closing_fence: 
                        # Strict Stripping
                        if len(sub_line) >= fence_indent_len:
                            clean_content = sub_line[fence_indent_len:].rstrip()
                        else:
                            clean_content = sub_line.strip()

                        has_bullet = False
                        
                        if is_opening_fence:
                            if clean_content.strip().startswith("- "):
                                clean_content = clean_content.strip()[2:]
                                has_bullet = True
                            elif sub_line.replace('\t', '    ').strip().startswith("- "):
                                has_bullet = True
                                if clean_content.strip().startswith("- "):
                                    clean_content = clean_content.strip()[2:]
                        
                else:
                    clean_content = content_part
                    has_bullet = False
                    if not in_code_block and content_part.startswith("- "):
                        clean_content = content_part[2:]
                        has_bullet = True
                    
                    if clean_content.strip() == "```" or clean_content.strip().startswith("```"):
                            has_bullet = False 
                    
                    if ":: " in clean_content:
                            prop_match = re.match(r'^[a-zA-Z0-9-_]+::', clean_content)
                            if prop_match:
                                j += 1
                                continue

                if not in_code_block:
                        clean_content = sanitize_content_links(clean_content)
                
                is_header = not in_code_block and clean_content.startswith("#")
                content_level = max(0, relative_tabs - 1)
                spaces_count = content_level * 2
                indent_str = " " * spaces_count
                
                if is_closing_fence:
                    articles_lines = f"{indent_str}  ```"
                    fence_indent_len = 0
                    
                elif in_code_block:
                    if is_opening_fence:
                        clean_content = clean_content.lower().strip()
                    
                    if has_bullet:
                        articles_lines = f"{indent_str}- {clean_content}"
                    else:
                        articles_lines = f"{indent_str}  {clean_content}"
                        
                elif has_bullet:
                    articles_lines = f"{indent_str}- {clean_content}"
                else:
                    if is_header:
                        articles_lines = f"{indent_str}- {clean_content}"
                    else:
                            articles_lines = f"{indent_str}  {clean_content}"
                    
                block_content.append(articles_lines)
                j += 1
            
            articles.append(Article(
                title=raw_title,
                frontmatter=frontmatter_raw,
                body="\n".join(block_content),
                source_file=filepath.name,
                type="block"
            ))
            
            i = j 
        else:
            i += 1
    return articles

def _parse_legacy_file(filepath: Path, content: str) -> Optional[Article]:
    end_marker = content.find("---", 3)
    if end_marker != -1:
        try:
            fm_str = content[3:end_marker]
            fm_str = re.sub(r'^(\w+)::(.*)$', r'\1:\2', fm_str, flags=re.MULTILINE)
            frontmatter = yaml.safe_load(fm_str)
            
            is_draft = frontmatter.get("draft", False)
            if isinstance(is_draft, str):
                is_draft = is_draft.lower() == "true"
            
            if not is_draft and frontmatter:
                body = content[end_marker+3:].strip()
                return Article(
                    title=frontmatter.get("title", filepath.stem),
                    frontmatter=frontmatter,
                    body=body,
                    source_file=filepath.name,
                    type="file"
                )
        except Exception as e:
            print(f"  ⚠️ YAML Parsing Error {filepath.name}: {e}")
    return None
