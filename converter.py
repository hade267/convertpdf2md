
import os
import re
import uuid
import unicodedata
import pathlib
import pymupdf4llm
import pymupdf


class DocMeta:

    def __init__(self):
        self.doc_id = ""
        self.title = ""
        self.date = ""
        self.signed_by = ""
        self.organization = ""
        self.custom_fields = {}                                          

    def generate_id(self):
        if not self.doc_id:
            self.doc_id = str(uuid.uuid4())[:8].upper()

    def to_markdown(self) -> str:
        self.generate_id()
        lines = [
            "# DocMeta",
            f"- **doc_id**: {self.doc_id}",
            f"- **title**: {self.title}",
            f"- **date**: {self.date}",
            f"- **signed_by**: {self.signed_by}",
            f"- **organization**: {self.organization}",
        ]
                            
        for key, value in self.custom_fields.items():
            if key.strip() and value.strip():
                lines.append(f"- **{key.strip()}**: {value.strip()}")
        lines.extend(["", "---", ""])
        return "\n".join(lines)

    @staticmethod
    def extract_from_pdf(doc) -> "DocMeta":
        meta = DocMeta()
        pdf_meta = doc.metadata or {}

        meta.title = pdf_meta.get("title", "") or ""
        meta.date = pdf_meta.get("creationDate", "") or ""
        meta.signed_by = pdf_meta.get("author", "") or ""
        meta.organization = pdf_meta.get("producer", "") or ""

                                                                 
        if meta.date.startswith("D:"):
            raw = meta.date[2:]
            if len(raw) >= 8:
                meta.date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"

        meta.generate_id()
        return meta


class ConversionOptions:

    def __init__(self):
        self.write_images = True
        self.image_path = ""
        self.table_strategy = "lines_strict"                                       
        self.pages = None                       
        self.ignore_graphics = False
        self.ignore_images = False
        self.force_text = False
        self.header_detection = "auto"                         
        self.max_heading_level = 5                                

                         
        self.auto_extract_meta = True                                      
        self.doc_meta = None                                           

                              
        self.filename_prefix = ""                               
        self.filename_suffix = ""                              
        self.show_page_breaks = False                                              
        self.remove_page_numbers = True                                                   
        self.bold_keywords = ""                                                    
        self.output_encoding = "utf-8"                        

                                
        self.margins = 0                                                                                         
        self.dpi = 150                                          
        self.fontsize_limit = 3                                                             
        self.dehyphenate = True                                                   
        self.remove_headers_footers = True                                              
        self.normalize_unicode = True                                              
        self.fix_broken_paragraphs = True                                    
        
                              
        self.enable_ai = False
        self.ai_provider = "ChatGPT"
        self.ai_api_key = ""
        self.ai_task = "Tóm tắt"


class ConversionResult:

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.md_path = ""
        self.markdown_text = ""
        self.success = False
        self.error_message = ""
        self.page_count = 0
        self.doc_meta = None
        self.table_count = 0


class TextCleaner:

                                     
    LIGATURE_MAP = {
        'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl',
        'ﬅ': 'st', 'ﬆ': 'st', '\ufb01': 'fi', '\ufb02': 'fl',
        '\u2018': "'", '\u2019': "'",                
        '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-',              
        '\u00a0': ' ',                      
        '\u200b': '',                     
        '\u200c': '',                          
        '\u200d': '',                      
        '\ufeff': '',        
    }

    def __init__(self, dehyphenate: bool = True,
                 normalize_unicode: bool = True,
                 fix_broken_paragraphs: bool = True,
                 remove_headers_footers: bool = True):
        self.dehyphenate = dehyphenate
        self.normalize_unicode = normalize_unicode
        self.fix_broken_paragraphs = fix_broken_paragraphs
        self.remove_headers_footers = remove_headers_footers

    def clean(self, text: str) -> str:
        if self.normalize_unicode:
            text = self._normalize_unicode(text)
            text = self._fix_ligatures(text)

        text = self._fix_special_chars(text)

        if self.dehyphenate:
            text = self._dehyphenate(text)

        if self.fix_broken_paragraphs:
            text = self._fix_broken_paragraphs_fn(text)

        if self.remove_headers_footers:
            text = self._remove_repeated_headers_footers(text)

        text = self._remove_duplicate_lines(text)

        return text

    def _normalize_unicode(self, text: str) -> str:
        return unicodedata.normalize('NFC', text)

    def _fix_ligatures(self, text: str) -> str:
        for ligature, replacement in self.LIGATURE_MAP.items():
            text = text.replace(ligature, replacement)
        return text

    def _fix_special_chars(self, text: str) -> str:
                                             
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
                                    
        text = text.replace('•', '- ')
        text = text.replace('●', '- ')
        text = text.replace('○', '  - ')
        text = text.replace('■', '- ')
        text = text.replace('▪', '  - ')
        text = text.replace('►', '- ')
        text = text.replace('→', '->')
        return text

    def _dehyphenate(self, text: str) -> str:
                                                              
        text = re.sub(
            r'(\w)-\s*\n\s*(\w)',
            r'\1\2',
            text
        )
        return text

    def _fix_broken_paragraphs_fn(self, text: str) -> str:
        lines = text.split('\n')
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.rstrip()

                                     
            if (i + 1 < len(lines)
                    and stripped                             
                    and not stripped.startswith('#')                         
                    and not stripped.startswith('- ')                     
                    and not stripped.startswith('* ')                     
                    and not stripped.startswith('|')                      
                    and not stripped.startswith('<!-')                                   
                    and not stripped.startswith('>')                            
                    and not stripped.endswith(':')                               
                    and not stripped.endswith('.')                                 
                    and not stripped.endswith('!')                                 
                    and not stripped.endswith('?')                                 
                    and not stripped.endswith(';')                                 
                    ):
                next_line = lines[i + 1].strip()
                                                              
                if (next_line
                        and next_line[0].islower()
                        and not next_line.startswith('#')
                        and not next_line.startswith('- ')
                        and not next_line.startswith('* ')
                        and not next_line.startswith('|')
                        and not next_line.startswith('<!-')):
                    result.append(stripped + ' ' + next_line)
                    i += 2
                    continue

            result.append(line)
            i += 1

        return '\n'.join(result)

    def _remove_repeated_headers_footers(self, text: str) -> str:
        lines = text.split('\n')
                                               
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) < 80 and not stripped.startswith('#'):
                line_counts[stripped] = line_counts.get(stripped, 0) + 1

                                                              
        repeated = {line for line, count in line_counts.items() if count >= 3}

        if repeated:
            lines = [l for l in lines if l.strip() not in repeated]

        return '\n'.join(lines)

    def _remove_duplicate_lines(self, text: str) -> str:
        lines = text.split('\n')
        result = []
        prev = None
        for line in lines:
            stripped = line.strip()
            if stripped != prev or not stripped:
                result.append(line)
            prev = stripped
        return '\n'.join(result)


class MarkdownPostProcessor:

                                                                         
    TABLE_PATTERN = re.compile(
        r'((?:^\|.+\|[ \t]*\n)+)',
        re.MULTILINE
    )

                         
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def __init__(self, max_heading_level: int = 5,
                 show_page_breaks: bool = False,
                 remove_page_numbers: bool = True,
                 bold_keywords: str = "",
                 text_cleaner: TextCleaner = None):
        self.max_heading_level = max_heading_level
        self.show_page_breaks = show_page_breaks
        self.remove_page_numbers = remove_page_numbers
        self.bold_keywords = [k.strip() for k in bold_keywords.split(",") if k.strip()] if bold_keywords else []
        self.text_cleaner = text_cleaner

    def process(self, md_text: str, doc_meta: DocMeta = None) -> tuple:
                                                   
        if self.text_cleaner:
            md_text = self.text_cleaner.clean(md_text)

                                            
        md_text, table_count = self._replace_tables_with_placeholder(md_text)

                                                                     
        md_text = self._normalize_headings(md_text)

                                   
        md_text = self._handle_page_breaks(md_text)

                                  
        if self.remove_page_numbers:
            md_text = self._remove_page_numbers(md_text)

                                
        if self.bold_keywords:
            md_text = self._apply_bold_keywords(md_text)

                                           
        md_text = self._clean_whitespace(md_text)

                                     
        if doc_meta:
            md_text = doc_meta.to_markdown() + md_text

        return md_text, table_count

    def _replace_tables_with_placeholder(self, md_text: str) -> tuple:
        table_count = 0

        def replace_table(match):
            nonlocal table_count
            table_count += 1
            table_content = match.group(1)

                                
            rows = [r for r in table_content.strip().split('\n') if r.strip()]
            num_rows = len(rows)
            num_cols = 0
            if rows:
                num_cols = rows[0].count('|') - 1
                if num_cols < 0:
                    num_cols = 0

                                                                             
            data_rows = num_rows
            for row in rows:
                stripped = row.strip().strip('|').strip()
                if re.match(r'^[\s\-:|]+$', stripped):
                    data_rows -= 1

            placeholder = (
                f"\n<!-- TABLE_{table_count:03d} | rows={data_rows} | cols={num_cols} -->\n"
                f"**[Bảng {table_count}]** *(chưa parse — {data_rows} hàng × {num_cols} cột)*\n"
                f"<!-- /TABLE_{table_count:03d} -->\n"
            )
            return placeholder

        md_text = self.TABLE_PATTERN.sub(replace_table, md_text)
        return md_text, table_count

    def _normalize_headings(self, md_text: str) -> str:
        max_level = self.max_heading_level

        def replace_heading(match):
            hashes = match.group(1)
            title = match.group(2)
            level = len(hashes)

                                   
            if level > max_level:
                level = max_level

            return f"{'#' * level} {title}"

        return self.HEADING_PATTERN.sub(replace_heading, md_text)

    def _handle_page_breaks(self, md_text: str) -> str:
                                                       
        page_break_patterns = [
            r'\n-{5,}\n',                           
            r'\x0c',                                    
            r'\n\*{5,}\n',                           
        ]
        for pattern in page_break_patterns:
            if self.show_page_breaks:
                md_text = re.sub(pattern, '\n\n<!-- PAGE_BREAK -->\n\n', md_text)
            else:
                md_text = re.sub(pattern, '\n\n', md_text)
        return md_text

    def _remove_page_numbers(self, md_text: str) -> str:
                                                                  
        md_text = re.sub(r'^\s*\d{1,4}\s*$', '', md_text, flags=re.MULTILINE)
        return md_text

    def _apply_bold_keywords(self, md_text: str) -> str:
        for keyword in self.bold_keywords:
                                                                                  
            escaped = re.escape(keyword)
                                                                       
            md_text = re.sub(
                rf'(?<!\*\*)(?<!#\s)(?<!<!--\s)\b({escaped})\b(?!\*\*)',
                rf'**\1**',
                md_text,
                flags=re.IGNORECASE
            )
        return md_text

    def _clean_whitespace(self, md_text: str) -> str:
                                            
        md_text = re.sub(r'\n{4,}', '\n\n\n', md_text)

                                             
        md_text = re.sub(r'([^\n])\n(#{1,5}\s)', r'\1\n\n\2', md_text)

        return md_text.strip() + "\n"


class PDFConverter:

    TABLE_STRATEGIES = ["lines_strict", "lines", "text", "explicit"]
    HEADER_MODES = ["auto", "toc", "font", "none"]

    def __init__(self):
        self._progress_callback = None
        self._log_callback = None

    def set_progress_callback(self, callback):
        self._progress_callback = callback

    def set_log_callback(self, callback):
        self._log_callback = callback

    def _log(self, message: str):
        if self._log_callback:
            self._log_callback(message)

    def _progress(self, current: int, total: int, message: str = ""):
        if self._progress_callback:
            self._progress_callback(current, total, message)

    def convert_file(self, pdf_path: str, output_dir: str, options: ConversionOptions = None) -> ConversionResult:
        if options is None:
            options = ConversionOptions()

        result = ConversionResult(pdf_path)
        filename = os.path.splitext(os.path.basename(pdf_path))[0]

        try:
            self._log(f"📄 Đang mở: {os.path.basename(pdf_path)}")

                    
            doc = pymupdf.open(pdf_path)
            result.page_count = len(doc)
            self._log(f"   Số trang: {result.page_count}")

                           
            if options.doc_meta:
                doc_meta = options.doc_meta
                self._log(f"   DocMeta: sử dụng metadata từ người dùng")
            elif options.auto_extract_meta:
                doc_meta = DocMeta.extract_from_pdf(doc)
                                                                  
                if not doc_meta.title:
                    doc_meta.title = filename
                self._log(f"   DocMeta: trích xuất tự động (doc_id={doc_meta.doc_id})")
            else:
                doc_meta = DocMeta()
                doc_meta.title = filename
                doc_meta.generate_id()

            result.doc_meta = doc_meta

                                       
            hdr_info = self._get_header_info(doc, options)

                                 
            image_path = options.image_path
            if not image_path and options.write_images:
                image_path = os.path.join(output_dir, f"{filename}_images")
                os.makedirs(image_path, exist_ok=True)

                         
            pages = None
            if options.pages:
                pages = self._parse_pages(options.pages, result.page_count)

            self._log(f"   Chiến lược bảng: {options.table_strategy}")
            self._log(f"   Trích xuất ảnh: {'Có' if options.write_images else 'Không'}")
            self._log(f"   Max heading level: {options.max_heading_level}")
            self._log(f"   Margins: {options.margins} pt")
            self._log(f"   DPI: {options.dpi}")
            self._log(f"   Fontsize limit: {options.fontsize_limit} pt")
            if options.dehyphenate:
                self._log(f"   Dehyphenate: Có (nối từ bị ngắt dòng)")
            if options.remove_headers_footers:
                self._log(f"   Xóa header/footer lặp: Có")
            if options.normalize_unicode:
                self._log(f"   Normalize Unicode: Có")
            if options.fix_broken_paragraphs:
                self._log(f"   Fix broken paragraphs: Có")
            if options.bold_keywords:
                self._log(f"   Bold keywords: {options.bold_keywords}")
            if options.remove_page_numbers:
                self._log(f"   Xóa số trang: Có")

                           
            margins_val = options.margins
            if isinstance(margins_val, str) and margins_val.strip():
                try:
                    parts = [int(x.strip()) for x in margins_val.split(',')]
                    if len(parts) == 1:
                        margins_val = parts[0]
                    elif len(parts) == 4:
                        margins_val = tuple(parts)
                    else:
                        margins_val = 0
                except ValueError:
                    margins_val = 0
            elif isinstance(margins_val, str):
                margins_val = 0

                                     
            self._log("   🔄 Đang chuyển đổi PDF → raw Markdown...")

                                                  
            to_md_kwargs = dict(
                pages=pages,
                hdr_info=hdr_info,
                write_images=options.write_images,
                image_path=image_path if options.write_images else "",
                table_strategy=options.table_strategy,
                ignore_graphics=options.ignore_graphics,
                ignore_images=options.ignore_images,
                force_text=options.force_text,
                dpi=options.dpi,
            )

                                  
            if margins_val:
                to_md_kwargs['margins'] = margins_val

                                         
            if options.fontsize_limit > 0:
                to_md_kwargs['fontsize_limit'] = options.fontsize_limit

            md_text = pymupdf4llm.to_markdown(doc, **to_md_kwargs)

                                                     
            text_cleaner = TextCleaner(
                dehyphenate=options.dehyphenate,
                normalize_unicode=options.normalize_unicode,
                fix_broken_paragraphs=options.fix_broken_paragraphs,
                remove_headers_footers=options.remove_headers_footers,
            )
            self._log("   🧹 Text cleaning: ligature, dehyphenate, unicode, paragraphs...")

                                   
            self._log("   🔧 Post-processing: DocMeta + heading + table placeholder...")
            processor = MarkdownPostProcessor(
                max_heading_level=options.max_heading_level,
                show_page_breaks=options.show_page_breaks,
                remove_page_numbers=options.remove_page_numbers,
                bold_keywords=options.bold_keywords,
                text_cleaner=text_cleaner,
            )
            md_text, table_count = processor.process(md_text, doc_meta)
            result.table_count = table_count

            if table_count > 0:
                self._log(f"   📊 Phát hiện {table_count} bảng → đã thay bằng placeholder")

                                      
            if getattr(options, "enable_ai", False) and getattr(options, "ai_api_key", "").strip():
                self._log(f"   🤖 Đang chạy AI ({options.ai_provider} - {options.ai_task})...")
                try:
                    from ai_processor import AIProcessor
                    ai_proc = AIProcessor(
                        provider=options.ai_provider,
                        api_key=options.ai_api_key,
                        task=options.ai_task
                    )
                    md_text = ai_proc.process(md_text, log_callback=self._log)
                    self._log("   🤖 Hoàn thành xử lý AI.")
                except Exception as e:
                    self._log(f"   ⚠️ Lỗi AI: {str(e)}")
                    md_text += f"\n\n> [!CAUTION]\n> **AI Processing Failed:** {str(e)}\n"

                                                  
            out_name = f"{options.filename_prefix}{filename}{options.filename_suffix}.md"
            md_path = os.path.join(output_dir, out_name)
            pathlib.Path(md_path).write_bytes(md_text.encode(options.output_encoding))

            result.markdown_text = md_text
            result.md_path = md_path
            result.success = True
            self._log(f"   ✅ Hoàn thành: {out_name}")

            doc.close()

        except Exception as e:
            result.error_message = str(e)
            result.success = False
            self._log(f"   ❌ Lỗi: {e}")

        return result

    def convert_batch(self, pdf_paths: list, output_dir: str, options: ConversionOptions = None) -> list:
        os.makedirs(output_dir, exist_ok=True)
        results = []
        total = len(pdf_paths)

        self._log(f"🚀 Bắt đầu chuyển đổi {total} file...")
        self._progress(0, total, "Đang bắt đầu...")

        for i, pdf_path in enumerate(pdf_paths):
            self._progress(i, total, f"Đang xử lý: {os.path.basename(pdf_path)}")
            result = self.convert_file(pdf_path, output_dir, options)
            results.append(result)
            self._progress(i + 1, total, f"Xong: {os.path.basename(pdf_path)}")

        success_count = sum(1 for r in results if r.success)
        fail_count = total - success_count
        total_tables = sum(r.table_count for r in results)
        self._log(f"\n📊 Kết quả: {success_count}/{total} thành công, {fail_count} lỗi")
        if total_tables > 0:
            self._log(f"📋 Tổng bảng placeholder: {total_tables}")
        self._progress(total, total, "Hoàn thành!")

        return results

    def _get_header_info(self, doc, options: ConversionOptions):
        mode = options.header_detection

        if mode == "none":
            return False
        elif mode == "toc":
            try:
                return pymupdf4llm.TocHeaders(doc)
            except Exception:
                self._log("   ⚠ TOC không khả dụng, dùng auto")
                return None
        elif mode == "font":
            try:
                return pymupdf4llm.IdentifyHeaders(doc)
            except Exception:
                self._log("   ⚠ Font-based detection không khả dụng, dùng auto")
                return None
        else:        
            return None

    def _parse_pages(self, pages_str: str, total_pages: int) -> list:
        pages = []
        try:
            for part in pages_str.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = part.split("-")
                    start = max(1, int(start.strip()))
                    end = min(total_pages, int(end.strip()))
                    pages.extend(range(start - 1, end))
                else:
                    page = int(part) - 1
                    if 0 <= page < total_pages:
                        pages.append(page)
        except ValueError:
            return None

        return sorted(set(pages)) if pages else None
