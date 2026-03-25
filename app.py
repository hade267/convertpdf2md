import flet as ft
import os
import threading
from converter import PDFConverter, ConversionOptions, DocMeta

class FletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PDF to Markdown Converter"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.window.min_width = 1000
        self.page.window.min_height = 650

        self.converter = PDFConverter()
        self.converter.set_log_callback(self._on_log)
        self.converter.set_progress_callback(self._on_progress)

        self.selected_files = []
        self.output_dir = ""
        self.is_converting = False

        self._build_ui()

    def _build_ui(self):
                             
        self.colors = {
            "accent": "#6C63FF",
            "bg_app": "#0F172A",
            "bg_island": "#1E293B",
            "bg_input": "#0B0F19",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "border": "#334155",
            "success": "#00C48C",
            "error": "#FF6B6B",
            "warning": "#FFB946"
        }
        self.page.bgcolor = self.colors["bg_app"]

                                                                              
                                  
                
        title_card = self._build_card([
            ft.Text("📄 PDF → MD", size=22, weight=ft.FontWeight.BOLD, color=self.colors["accent"]),
            ft.Text("Chuyển đổi PDF sang Markdown", size=12, color=self.colors["text_secondary"])
        ])

                        
        self.file_count_label = ft.Text("Chưa chọn file nào", size=12, color=self.colors["text_secondary"])
        self.file_listbox = ft.TextField(multiline=True, read_only=True, height=80, text_size=11,
                                         border_color=self.colors["border"], bgcolor=self.colors["bg_input"])
        file_card = self._build_card([
            self._section_label("CHỌN FILE"),
            ft.Row([
                ft.ElevatedButton("Chọn File PDF", on_click=self._choose_files, bgcolor=self.colors["accent"], color=ft.Colors.WHITE),
                ft.OutlinedButton("Thư mục", on_click=self._choose_folder)
            ]),
            self.file_count_label,
            self.file_listbox
        ])

                    
        self.output_label = ft.Text("Mặc định: cùng thư mục PDF", size=11, color=self.colors["text_secondary"])
        outdir_card = self._build_card([
            self._section_label("THƯ MỤC OUTPUT"),
            ft.ElevatedButton("Chọn thư mục lưu", on_click=self._choose_outdir),
            self.output_label
        ])

                 
        self.auto_meta_var = ft.Checkbox(label="Tự động trích xuất từ PDF", value=True, on_change=self._toggle_meta_fields)
        self.meta_doc_id = self._input("Doc ID (auto nếu trống)")
        self.meta_title = self._input("Tiêu đề tài liệu")
        self.meta_date = self._input("Ngày (VD: 2024-01-15)")
        self.meta_signed_by = self._input("Người ký")
        self.meta_org = self._input("Tổ chức")
        self.meta_custom = ft.TextField(multiline=True, height=60, text_size=11, hint_text="Trường tùy chỉnh (key=value, mỗi dòng 1 trường)",
                                        border_color=self.colors["border"], bgcolor=self.colors["bg_input"])
        
        self.meta_fields = [self.meta_doc_id, self.meta_title, self.meta_date, self.meta_signed_by, self.meta_org, self.meta_custom]
        for f in self.meta_fields:
            f.disabled = True

        meta_card = self._build_card([
            self._section_label("DOCMETA (tùy chọn)"),
            self.auto_meta_var,
            *self.meta_fields[:-1],
            ft.Text("Trường tùy chỉnh (key=value):", size=11, color=self.colors["text_secondary"]),
            self.meta_custom
        ])

                          
        self.table_strategy = self._dropdown("Phát hiện bảng:", PDFConverter.TABLE_STRATEGIES, "lines_strict")
        self.header_mode = self._dropdown("Phát hiện heading:", PDFConverter.HEADER_MODES, "auto")
        self.max_heading = self._dropdown("Max heading level:", ["3", "4", "5", "6"], "5")
        self.pages_entry = self._input("Trang (VD: 1-3, 5):", hint="Tất cả trang")
        self.extract_images = ft.Checkbox(label="Trích xuất hình ảnh", value=True)
        self.force_text = ft.Checkbox(label="Ép trích xuất text (PDF scan)", value=False)
        
        settings_card = self._build_card([
            self._section_label("CÀI ĐẶT CHUYỂN ĐỔI"),
            self.table_strategy, self.header_mode, self.max_heading,
            ft.Text("Trang:", size=12), self.pages_entry,
            self.extract_images, self.force_text
        ])

                        
        self.prefix_entry = self._input("Tiền tố filename")
        self.suffix_entry = self._input("Hậu tố filename")
        self.keywords_entry = self._input("Từ khóa in đậm (cách bằng dấu phẩy)")
        self.show_page_breaks = ft.Checkbox(label="Hiện dấu ngắt trang (PAGE_BREAK)", value=False)
        self.remove_page_numbers = ft.Checkbox(label="Xóa số trang tự động", value=True)
        self.output_encoding = self._dropdown("Encoding output:", ["utf-8", "utf-8-sig", "utf-16", "latin-1"], "utf-8")

        custom_card = self._build_card([
            self._section_label("TÙY CHỈNH THÊM"),
            ft.Row([self.prefix_entry, ft.Text("+ gốc +"), self.suffix_entry]),
            self.keywords_entry,
            self.show_page_breaks,
            self.remove_page_numbers,
            self.output_encoding
        ])

                  
        self.margins_entry = self._input("Margins (pt)", hint="0 hoặc left,top,right,bottom")
        self.dpi_var = self._dropdown("DPI:", ["72", "96", "150", "200", "300"], "150")
        self.fontsize_limit = self._dropdown("Font min (pt):", ["0", "1", "2", "3", "4", "5"], "3")
        self.dehyphenate = ft.Checkbox(label="Nối từ bị ngắt dòng (dehyphenate)", value=True)
        self.remove_hf = ft.Checkbox(label="Xóa header/footer lặp lại", value=True)
        self.normalize_unicode = ft.Checkbox(label="Chuẩn hóa Unicode & ligature", value=True)
        self.fix_paragraphs = ft.Checkbox(label="Nối đoạn văn bị ngắt dòng", value=True)

        acc_card = self._build_card([
            self._section_label("ĐỘ CHÍNH XÁC"),
            self.margins_entry,
            ft.Row([self.dpi_var, self.fontsize_limit]),
            self.dehyphenate, self.remove_hf, self.normalize_unicode, self.fix_paragraphs
        ])

                        
        self.enable_ai = ft.Switch(label="Bật xử lý AI (Tóm tắt, Dịch...)", value=False, on_change=self._toggle_ai_fields)
        self.ai_provider = self._dropdown("Nhà cung cấp AI:", ["ChatGPT (gpt-4o-mini) - Tối ưu nhất", "Gemini (1.5-flash) - Tốt cho file dài", "NVIDIA (Llama3-70b) - Tốc độ cao"], "ChatGPT (gpt-4o-mini) - Tối ưu nhất")
        self.ai_task = self._dropdown("Tác vụ:", ["Tóm tắt", "Dịch sang Tiếng Việt", "Sửa lỗi OCR (Proofread)", "Tối ưu hóa cho RAG (Làm sạch Markdown)"], "Tối ưu hóa cho RAG (Làm sạch Markdown)")
        self.ai_apikey = self._input("API Key (Bắt buộc nếu dùng AI)", password=True)
        
        self.ai_fields = [self.ai_provider, self.ai_task, self.ai_apikey]
        for f in self.ai_fields:
            f.disabled = True

        ai_card = self._build_card([
            self._section_label("TÍCH HỢP AI"),
            self.enable_ai,
            *self.ai_fields
        ])

                 
        self.convert_btn = ft.ElevatedButton(
            "CHUYỂN ĐỔI", 
            bgcolor=self.colors["success"], 
            color=ft.Colors.WHITE, 
            height=50,
            on_click=self._start_conversion
        )
        self.clear_btn = ft.OutlinedButton(
            "Xóa tất cả",
            on_click=self._clear_all
        )

        sidebar_col = ft.Column([
            title_card, file_card, outdir_card, meta_card, settings_card, custom_card, acc_card, ai_card,
            self.convert_btn, self.clear_btn
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

        sidebar = ft.Container(
            content=sidebar_col,
            width=360,
            padding=10
        )

                                    
        self.status_label = ft.Text("Sẵn sàng chuyển đổi", size=16, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"])
        self.stats_label = ft.Text("", size=12, color=self.colors["text_secondary"])
        
        header = ft.Container(
            content=ft.Row([self.status_label, self.stats_label], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=self.colors["bg_island"],
            padding=15,
            border_radius=10
        )

              
        self.preview_tb = ft.TextField(multiline=True, read_only=True, expand=True, text_size=13,
                                       border_color=self.colors["border"], bgcolor=self.colors["bg_input"],
                                       value="Chọn file PDF và nhấn 'Chuyển Đổi' để bắt đầu...")
        self.log_tb = ft.TextField(multiline=True, read_only=True, expand=True, text_size=12,
                                   border_color=self.colors["border"], bgcolor=self.colors["bg_input"])
        self.results_tb = ft.TextField(multiline=True, read_only=True, expand=True, text_size=12,
                                       border_color=self.colors["border"], bgcolor=self.colors["bg_input"])

        self.tab_bar_view = ft.TabBarView(
            expand=True,
            controls=[
                ft.Container(content=self.preview_tb, padding=10),
                ft.Container(content=self.log_tb, padding=10),
                ft.Container(content=self.results_tb, padding=10),
            ]
        )

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            length=3,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Preview Markdown"),
                            ft.Tab(label="Log"),
                            ft.Tab(label="Kết quả"),
                        ]
                    ),
                    self.tab_bar_view,
                ]
            )
        )

        tab_container = ft.Container(
            content=tabs,
            bgcolor=self.colors["bg_island"],
            border_radius=10,
            expand=True,
            padding=10
        )

                  
        self.progress_label = ft.Text("Chờ chuyển đổi...", size=12, color=self.colors["text_secondary"])
        self.progress_percent = ft.Text("0%", size=12, weight=ft.FontWeight.BOLD, color=self.colors["accent"])
        self.progressbar = ft.ProgressBar(value=0, color=self.colors["accent"], bgcolor=self.colors["bg_input"], height=8)

        progress_frame = ft.Container(
            content=ft.Column([
                ft.Row([self.progress_label, self.progress_percent], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.progressbar
            ]),
            bgcolor=self.colors["bg_island"],
            padding=15,
            border_radius=10
        )

        main_col = ft.Column([
            header,
            tab_container,
            progress_frame
        ], expand=True, spacing=15)

                     
        self.page.add(
            ft.Row([
                sidebar,
                main_col
            ], expand=True)
        )

                   

    def _build_card(self, controls):
        return ft.Container(
            content=ft.Column(controls, spacing=10),
            bgcolor=self.colors["bg_island"],
            padding=15,
            border_radius=15
        )

    def _section_label(self, text):
        return ft.Text(text, size=13, weight=ft.FontWeight.BOLD, color=self.colors["text_secondary"])

    def _input(self, label, hint="", password=False):
        return ft.TextField(label=label, hint_text=hint, password=password, height=45, text_size=12,
                            border_color=self.colors["border"], bgcolor=self.colors["bg_input"])

    def _dropdown(self, label, options, default):
        opts = [ft.dropdown.Option(o) for o in options]
        return ft.Dropdown(label=label, options=opts, value=default, height=55, text_size=12,
                           border_color=self.colors["border"], bgcolor=self.colors["bg_input"])

                   

    def _toggle_meta_fields(self, e):
        disabled = self.auto_meta_var.value
        for f in self.meta_fields:
            f.disabled = disabled
        self.page.update()

    def _toggle_ai_fields(self, e):
        disabled = not self.enable_ai.value
        for f in self.ai_fields:
            f.disabled = disabled
        self.page.update()

    async def _choose_files(self, e):
        files = await ft.FilePicker().pick_files(allow_multiple=True, allowed_extensions=["pdf"])
        if files:
            self.selected_files = [f.path for f in files if f.path.lower().endswith('.pdf')]
            self._update_file_list()

    async def _choose_folder(self, e):
        folder = await ft.FilePicker().get_directory_path()
        if folder:
            pdf_files = []
            for f in os.listdir(folder):
                if f.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(folder, f))
            if pdf_files:
                self.selected_files = sorted(pdf_files)
                self._update_file_list()

    async def _choose_outdir(self, e):
        path = await ft.FilePicker().get_directory_path()
        if path:
            self.output_dir = path
            self.output_label.value = path
            self.page.update()

    def _update_file_list(self):
        count = len(self.selected_files)
        self.file_count_label.value = f"Đã chọn {count} file"
        
        lines = []
        for i, f in enumerate(self.selected_files, 1):
            lines.append(f"{i}. {os.path.basename(f)}")
        self.file_listbox.value = "\n".join(lines)
        self.page.update()

    def _clear_all(self, e):
        self.selected_files = []
        self._update_file_list()
        self.log_tb.value = ""
        self.preview_tb.value = "Đã xóa toàn bộ. Chọn file để tiếp tục."
        self.results_tb.value = ""
        self.progressbar.value = 0
        self.progress_percent.value = "0%"
        self.progress_label.value = "Chờ chuyển đổi..."
        self.stats_label.value = ""
        self.page.update()

    def _get_options(self) -> ConversionOptions:
        options = ConversionOptions()
        options.table_strategy = self.table_strategy.value
        options.header_detection = self.header_mode.value
        options.write_images = self.extract_images.value
        options.force_text = self.force_text.value
        options.max_heading_level = int(self.max_heading.value)
        options.auto_extract_meta = self.auto_meta_var.value

        pages_text = self.pages_entry.value.strip() if self.pages_entry.value else ""
        if pages_text:
            options.pages = pages_text

        options.filename_prefix = self.prefix_entry.value.strip() if self.prefix_entry.value else ""
        options.filename_suffix = self.suffix_entry.value.strip() if self.suffix_entry.value else ""
        options.show_page_breaks = self.show_page_breaks.value
        options.remove_page_numbers = self.remove_page_numbers.value
        options.bold_keywords = self.keywords_entry.value.strip() if self.keywords_entry.value else ""
        options.output_encoding = self.output_encoding.value

        options.margins = self.margins_entry.value.strip() if self.margins_entry.value else ""
        options.dpi = int(self.dpi_var.value)
        options.fontsize_limit = int(self.fontsize_limit.value)
        options.dehyphenate = self.dehyphenate.value
        options.remove_headers_footers = self.remove_hf.value
        options.normalize_unicode = self.normalize_unicode.value
        options.fix_broken_paragraphs = self.fix_paragraphs.value

        options.enable_ai = self.enable_ai.value
        options.ai_provider = self.ai_provider.value
        options.ai_task = self.ai_task.value
        options.ai_api_key = self.ai_apikey.value.strip() if self.ai_apikey.value else ""

        if not options.auto_extract_meta:
            meta = DocMeta()
            meta.doc_id = self.meta_doc_id.value.strip() if self.meta_doc_id.value else ""
            meta.title = self.meta_title.value.strip() if self.meta_title.value else ""
            meta.date = self.meta_date.value.strip() if self.meta_date.value else ""
            meta.signed_by = self.meta_signed_by.value.strip() if self.meta_signed_by.value else ""
            meta.organization = self.meta_org.value.strip() if self.meta_org.value else ""

            custom_text = self.meta_custom.value.strip() if self.meta_custom.value else ""
            if custom_text:
                for line in custom_text.split("\n"):
                    line = line.strip()
                    if "=" in line:
                        k, _, v = line.partition("=")
                        meta.custom_fields[k.strip()] = v.strip()
            options.doc_meta = meta

        return options

    def _start_conversion(self, e):
        if self.is_converting:
            return
        if not self.selected_files:
            return

        out_dir = self.output_dir
        if not out_dir:
            out_dir = os.path.dirname(self.selected_files[0])

        self.is_converting = True
        self.convert_btn.disabled = True
        self.convert_btn.text = "Đang xử lý..."
        self.status_label.value = "Đang chuyển đổi..."
        self.status_label.color = self.colors["warning"]
        self.log_tb.value = ""
        self.page.update()

        options = self._get_options()

        def background_task():
            try:
                results = self.converter.convert_batch(self.selected_files.copy(), out_dir, options)
                self.page.run_task(self._on_conversion_complete, results)
            except Exception as ex:
                self.page.run_task(self._on_conversion_error, str(ex))

        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()

    async def _on_conversion_complete(self, results):
        self.is_converting = False
        self.convert_btn.disabled = False
        self.convert_btn.text = "CHUYỂN ĐỔI"

        success = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        total_tbl = sum(r.table_count for r in results)

        if failed:
            self.status_label.value = f"Có lỗi: {len(success)} OK, {len(failed)} Lỗi"
            self.status_label.color = self.colors["error"]
        else:
            self.status_label.value = "Hoàn tất!"
            self.status_label.color = self.colors["success"]

        self.stats_label.value = f"File: {len(results)} | Bảng: {total_tbl}"

        res_lines = []
        for r in results:
            if r.success:
                res_lines.append(f"[OK] {os.path.basename(r.original_file)}")
                res_lines.append(f"  -> {r.output_file}")
                res_lines.append(f"  -> Bảng: {r.table_count}, Ảnh: {r.image_count}")
                if r.ai_summary:
                    res_lines.append(f"  -> AI: {r.ai_summary}")
            else:
                res_lines.append(f"[ERROR] {os.path.basename(r.original_file)}")
                res_lines.append(f"  -> {r.error_msg}")
            res_lines.append("-" * 40)

        self.results_tb.value = "\n".join(res_lines)

        if success:
            last_file = success[-1]
            try:
                with open(last_file.output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 3000:
                        content = content[:3000] + "\n... (Nội dung quá dài, đã được cắt bớt hiển thị) ..."
                    self.preview_tb.value = content
            except Exception as ex:
                self.preview_tb.value = f"Không thể đọc file output: {ex}"

        self.progressbar.value = 1.0
        self.progress_percent.value = "100%"
        self.progress_label.value = "Xong."
        self.page.update()

    async def _on_conversion_error(self, err_msg):
        self.is_converting = False
        self.convert_btn.disabled = False
        self.convert_btn.text = "CHUYỂN ĐỔI"
        self.status_label.value = "Lỗi hệ thống"
        self.status_label.color = self.colors["error"]
        
        self.log_tb.value += f"\n[FATAL ERROR] {err_msg}\n"
        self.progressbar.value = 0
        self.progress_percent.value = "0%"
        self.progress_label.value = "Chuyển đổi bị lỗi ngắt quãng."
        self.page.update()

    def _on_log(self, msg: str):
        async def update_log():
            current = self.log_tb.value or ""
            self.log_tb.value = current + msg + "\n"
            self.page.update()
        self.page.run_task(update_log)

    def _on_progress(self, current, total, message):
        async def update_prog():
            p = current / total if total > 0 else 0
            p = min(1.0, max(0.0, p))
            
            self.progressbar.value = p
            self.progress_percent.value = f"{int(p * 100)}%"
            self.progress_label.value = f"File {current}/{total} | {message}"
            self.page.update()
        self.page.run_task(update_prog)

def main(page: ft.Page):
    app = FletApp(page)

if __name__ == "__main__":
    ft.app(target=main)
