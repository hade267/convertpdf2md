# 📄 PDF to Markdown Converter (PDF2MD)

Ứng dụng desktop chuyển đổi file PDF sang định dạng Markdown, hỗ trợ xử lý hàng loạt, tích hợp AI và đóng gói thành file `.exe` độc lập.

---

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Tính năng](#tính-năng)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt & Chạy từ mã nguồn](#cài-đặt--chạy-từ-mã-nguồn)
- [Giao diện người dùng](#giao-diện-người-dùng)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Tùy chọn chuyển đổi](#tùy-chọn-chuyển-đổi)
- [Tích hợp AI](#tích-hợp-ai)
- [DocMeta](#docmeta)
- [Đóng gói thành file EXE](#đóng-gói-thành-file-exe)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)

---

## Tổng quan

**PDF2MD** là ứng dụng desktop được xây dựng bằng Python và framework [Flet](https://flet.dev/), cho phép:

- Chuyển đổi một hoặc nhiều file PDF sang Markdown chuẩn.
- Tự động trích xuất metadata (tiêu đề, tác giả, ngày…) từ PDF và ghi vào phần đầu file `.md`.
- Xử lý hậu kỳ văn bản: loại bỏ header/footer lặp lại, chuẩn hóa Unicode, nối từ bị ngắt dòng, xóa số trang thừa, v.v.
- Tích hợp AI (ChatGPT, Gemini, NVIDIA) để tóm tắt, dịch, sửa lỗi OCR hoặc làm sạch Markdown cho RAG.
- Đóng gói thành file `.exe` độc lập (Windows) không cần cài Python.

---

## Tính năng

### Chuyển đổi PDF
| Tính năng | Mô tả |
|---|---|
| Xử lý hàng loạt | Chuyển đổi nhiều file PDF cùng lúc |
| Chọn thư mục | Tự động quét tất cả file PDF trong một thư mục |
| Trích xuất hình ảnh | Lưu hình ảnh nhúng trong PDF ra thư mục riêng |
| Phát hiện bảng | Hỗ trợ 4 chiến lược: `lines_strict`, `lines`, `text`, `explicit` |
| Phát hiện heading | 4 chế độ: `auto`, `toc`, `font`, `none` |
| Giới hạn cấp heading | Cài đặt mức heading tối đa (H3–H6) |
| Chọn trang | Chỉ chuyển đổi một số trang nhất định (VD: `1-3, 5`) |

### Xử lý văn bản sau chuyển đổi
| Tính năng | Mô tả |
|---|---|
| Dehyphenate | Nối lại các từ bị ngắt dòng do xuống hàng |
| Chuẩn hóa Unicode | Chuẩn hóa NFC và thay thế ligature (ﬁ→fi, …) |
| Nối đoạn văn bị ngắt | Tự động ghép dòng ngắt giữa chừng |
| Xóa header/footer | Loại bỏ các dòng lặp lại ≥ 3 lần trong tài liệu |
| Xóa số trang | Tự động xóa số trang đứng riêng trên dòng |
| Từ khóa in đậm | Tự động in đậm danh sách từ khóa tùy chỉnh |
| Dấu ngắt trang | Hiển thị hoặc ẩn ký hiệu `<!-- PAGE_BREAK -->` |
| Encoding output | Hỗ trợ `utf-8`, `utf-8-sig`, `utf-16`, `latin-1` |

### Tùy chỉnh tên file output
- Thêm **tiền tố** và/hoặc **hậu tố** vào tên file Markdown đầu ra.
  - Ví dụ: prefix `doc_` + file gốc `report` + suffix `_2024` → `doc_report_2024.md`

### DocMeta
- Tự động trích xuất hoặc nhập thủ công các metadata: `doc_id`, `title`, `date`, `signed_by`, `organization`, cùng các trường tùy chỉnh (key=value).
- Ghi vào phần đầu mỗi file `.md` theo chuẩn có cấu trúc.

### Tích hợp AI
- **Tóm tắt**: Tóm tắt nội dung văn bản.
- **Dịch sang Tiếng Việt**: Dịch toàn bộ nội dung.
- **Sửa lỗi OCR (Proofread)**: Sửa lỗi nhận dạng ký tự từ scan.
- **Tối ưu hóa cho RAG**: Làm sạch Markdown để phục vụ hệ thống RAG/AI.

---

## Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11 (khuyến nghị), macOS, Linux
- **Python**: 3.10 trở lên
- **Kết nối Internet**: Chỉ cần khi sử dụng tính năng AI

---

## Cài đặt & Chạy từ mã nguồn

### 1. Clone repository

```bash
git clone https://github.com/hade267/convertpdf2md.git
cd convertpdf2md
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Nội dung `requirements.txt`:

```
pymupdf4llm>=0.0.17
pymupdf>=1.25.0
flet>=0.80.0
litellm>=1.0.0
```

### 4. Chạy ứng dụng

```bash
python main.py
```

Cửa sổ ứng dụng sẽ tự động mở lên.

---

## Giao diện người dùng

Giao diện chia làm hai phần chính:

```
┌─────────────────────┬─────────────────────────────────────┐
│   THANH BÊN TRÁI    │         KHU VỰC CHÍNH                │
│  (Cài đặt & điều    │                                     │
│   khiển ~360px)     │  ┌─────────────────────────────┐   │
│                     │  │  Trạng thái & Thống kê       │   │
│ - Chọn File         │  └─────────────────────────────┘   │
│ - Thư mục Output    │                                     │
│ - DocMeta           │  ┌─────────────────────────────┐   │
│ - Cài đặt chuyển đổi│  │ Tab: Preview | Log | Kết quả│   │
│ - Tùy chỉnh thêm    │  └─────────────────────────────┘   │
│ - Độ chính xác      │                                     │
│ - Tích hợp AI       │  ┌─────────────────────────────┐   │
│                     │  │  Thanh tiến trình            │   │
│ [CHUYỂN ĐỔI]        │  └─────────────────────────────┘   │
│ [Xóa tất cả]        │                                     │
└─────────────────────┴─────────────────────────────────────┘
```

**Các tab khu vực chính:**
- **Preview Markdown**: Hiển thị nội dung Markdown của file cuối cùng được chuyển đổi thành công.
- **Log**: Ghi lại toàn bộ quá trình chuyển đổi theo thời gian thực.
- **Kết quả**: Danh sách tổng hợp kết quả (thành công / lỗi) của từng file.

---

## Hướng dẫn sử dụng

### Bước 1 – Chọn file PDF

Có hai cách:
- Nhấn **"Chọn File PDF"** để chọn một hoặc nhiều file `.pdf`.
- Nhấn **"Thư mục"** để chọn thư mục, ứng dụng sẽ tự động tìm tất cả file `.pdf` bên trong.

### Bước 2 – Chọn thư mục lưu output *(tùy chọn)*

- Nhấn **"Chọn thư mục lưu"** để chỉ định nơi lưu file `.md`.
- Nếu bỏ qua, file `.md` sẽ được lưu cùng thư mục với file PDF gốc.

### Bước 3 – Cấu hình tùy chọn *(tùy chọn)*

Xem chi tiết tại mục [Tùy chọn chuyển đổi](#tùy-chọn-chuyển-đổi).

### Bước 4 – Nhấn "CHUYỂN ĐỔI"

- Thanh tiến trình và tab **Log** sẽ cập nhật theo thời gian thực.
- Sau khi hoàn tất, tab **Kết quả** hiển thị danh sách file đã xử lý và trạng thái.
- Tab **Preview** hiển thị nội dung Markdown của file vừa chuyển đổi.

---

## Tùy chọn chuyển đổi

### Cài đặt chuyển đổi

| Tùy chọn | Giá trị mặc định | Mô tả |
|---|---|---|
| Phát hiện bảng | `lines_strict` | Chiến lược nhận diện bảng trong PDF |
| Phát hiện heading | `auto` | Cách xác định tiêu đề trong văn bản |
| Max heading level | `5` | Giới hạn cấp heading cao nhất (H1–H6) |
| Trang | *(tất cả)* | Chỉ chuyển đổi các trang chỉ định, VD: `1-3, 5` |
| Trích xuất hình ảnh | Bật | Lưu hình ảnh ra file riêng |
| Ép trích xuất text | Tắt | Dùng cho PDF scan không có text layer |

**Chiến lược phát hiện bảng (`table_strategy`):**
- `lines_strict` *(mặc định)*: Chỉ phát hiện bảng có đường kẻ rõ ràng. Độ chính xác cao nhất.
- `lines`: Phát hiện bảng dựa trên đường kẻ (kém chặt chẽ hơn).
- `text`: Phát hiện bảng dựa trên căn chỉnh cột text.
- `explicit`: Chỉ dùng vùng bảng được khai báo tường minh.

**Chế độ phát hiện heading (`header_detection`):**
- `auto` *(mặc định)*: Tự động phát hiện dựa trên cỡ chữ và vị trí.
- `toc`: Dùng mục lục (Table of Contents) của PDF.
- `font`: Dựa vào cỡ chữ để phân loại cấp heading.
- `none`: Không phát hiện heading, toàn bộ là nội dung thường.

### Tùy chỉnh thêm

| Tùy chọn | Mô tả |
|---|---|
| Tiền tố / Hậu tố filename | Thêm chuỗi ký tự vào đầu/cuối tên file output |
| Từ khóa in đậm | Danh sách từ khóa cách nhau bằng dấu phẩy, sẽ tự động được in đậm trong output |
| Hiện dấu ngắt trang | Thêm `<!-- PAGE_BREAK -->` tại vị trí ngắt trang |
| Xóa số trang tự động | Xóa các dòng chỉ chứa số trang |
| Encoding output | Định dạng mã hóa file output (`utf-8`, `utf-8-sig`, `utf-16`, `latin-1`) |

### Độ chính xác (nâng cao)

| Tùy chọn | Mặc định | Mô tả |
|---|---|---|
| Margins (pt) | `0` | Vùng lề bị bỏ qua khi trích xuất (left, top, right, bottom) |
| DPI | `150` | Độ phân giải render ảnh |
| Font min (pt) | `3` | Bỏ qua text có cỡ chữ nhỏ hơn giá trị này |
| Dehyphenate | Bật | Nối lại từ bị ngắt dòng bằng dấu gạch ngang |
| Xóa header/footer | Bật | Loại bỏ các dòng lặp lại ≥ 3 lần |
| Chuẩn hóa Unicode | Bật | Chuẩn hóa NFC, thay thế ligature |
| Nối đoạn văn bị ngắt | Bật | Ghép dòng ngắt giữa câu thành đoạn liền mạch |

---

## Tích hợp AI

Bật **"Tích hợp AI"** trong giao diện để xử lý văn bản Markdown đã chuyển đổi bằng AI.

### Nhà cung cấp được hỗ trợ

| Nhà cung cấp | Model | Biến môi trường | Ghi chú |
|---|---|---|---|
| **ChatGPT** | `gpt-4o-mini` | `OPENAI_API_KEY` | Tối ưu nhất, cân bằng chất lượng/chi phí |
| **Gemini** | `gemini-1.5-flash` | `GEMINI_API_KEY` | Tốt cho file văn bản dài |
| **NVIDIA** | `llama3-70b-instruct` | `NVIDIA_NIM_API_KEY` | Tốc độ xử lý cao |

### Các tác vụ AI

| Tác vụ | Mô tả |
|---|---|
| **Tóm tắt** | Tóm tắt các ý chính ngắn gọn, dễ hiểu |
| **Dịch sang Tiếng Việt** | Dịch toàn bộ nội dung, giữ nguyên cấu trúc Markdown |
| **Sửa lỗi OCR (Proofread)** | Sửa lỗi chính tả, lỗi nhận dạng ký tự từ scan |
| **Tối ưu hóa cho RAG** | Làm sạch Markdown để phục vụ hệ thống RAG/AI |

### Cách lấy API Key

- **OpenAI (ChatGPT)**: Tạo tại [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Google Gemini**: Tạo tại [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- **NVIDIA NIM**: Tạo tại [build.nvidia.com](https://build.nvidia.com)

### Xử lý văn bản dài (chunking)

Với văn bản vượt quá **15.000 ký tự**, AI Processor tự động:
1. Chia văn bản thành các đoạn (chunks) theo ranh giới đoạn văn.
2. Gửi từng chunk riêng lẻ đến API.
3. Thử lại tối đa 3 lần nếu gặp lỗi (với delay mũ: 1s, 2s, 4s).
4. Ghép kết quả lại thành văn bản hoàn chỉnh.

> **Lưu ý**: API Key được truyền qua biến môi trường trong phiên làm việc hiện tại và không được lưu lại sau khi tắt ứng dụng.

---

## DocMeta

**DocMeta** là phần metadata cấu trúc được chèn vào đầu mỗi file `.md`, giúp tổ chức và tìm kiếm tài liệu dễ dàng.

### Chế độ tự động

Khi bật **"Tự động trích xuất từ PDF"** (mặc định), ứng dụng đọc metadata từ chính file PDF:
- `title` ← `pdf.metadata["title"]`
- `date` ← `pdf.metadata["creationDate"]` (định dạng lại thành `YYYY-MM-DD`)
- `signed_by` ← `pdf.metadata["author"]`
- `organization` ← `pdf.metadata["producer"]`
- `doc_id` ← UUID 8 ký tự tự sinh

### Chế độ thủ công

Tắt "Tự động trích xuất" để nhập thủ công:

| Trường | Mô tả |
|---|---|
| Doc ID | Mã tài liệu (tự sinh UUID nếu để trống) |
| Tiêu đề | Tên tài liệu |
| Ngày | Ngày phát hành (VD: `2024-01-15`) |
| Người ký | Tên tác giả / người ký |
| Tổ chức | Tên tổ chức / đơn vị |
| Trường tùy chỉnh | Mỗi dòng một trường theo cú pháp `key=value` |

### Ví dụ output DocMeta

```markdown
# DocMeta
- **doc_id**: A1B2C3D4
- **title**: Báo cáo tài chính Q1 2024
- **date**: 2024-03-31
- **signed_by**: Nguyễn Văn A
- **organization**: Công ty ABC
- **department**: Phòng Tài chính

---
```

---

## Đóng gói thành file EXE

Ứng dụng hỗ trợ đóng gói thành file `.exe` độc lập cho Windows bằng **PyInstaller**.

### Yêu cầu

```bash
pip install pyinstaller
```

### Chạy lệnh build

```bash
python build.py
```

### Quá trình build

Script `build.py` sẽ tự động:
1. Gọi PyInstaller với cấu hình tối ưu.
2. Thu thập toàn bộ dependency: `pymupdf`, `pymupdf4llm`, `flet`, `litellm`.
3. Đóng gói thành **một file duy nhất** (`--onefile`) chế độ cửa sổ (`--windowed`).
4. Xuất ra file `dist/PDF2MD.exe`.

### Output

```
dist/
└── PDF2MD.exe    # File thực thi độc lập (~150-300 MB)
```

> **Lưu ý**: Quá trình build có thể mất vài phút. File `.exe` tạo ra không cần cài Python hay bất kỳ thư viện nào.

---

## Cấu trúc dự án

```
convertpdf2md/
├── main.py           # Entry point – khởi chạy ứng dụng Flet
├── app.py            # Giao diện người dùng (FletApp class)
├── converter.py      # Logic chuyển đổi PDF → Markdown
│                     #   ├── DocMeta       – Metadata tài liệu
│                     #   ├── ConversionOptions – Cấu hình chuyển đổi
│                     #   ├── ConversionResult  – Kết quả chuyển đổi
│                     #   ├── TextCleaner   – Làm sạch văn bản
│                     #   ├── MarkdownPostProcessor – Hậu xử lý Markdown
│                     #   └── PDFConverter  – Bộ chuyển đổi chính
├── ai_processor.py   # Tích hợp AI qua litellm
│                     #   └── AIProcessor   – Gọi API, chunking, retry
├── build.py          # Script đóng gói thành file EXE
└── requirements.txt  # Danh sách thư viện Python
```

### Luồng xử lý chính

```
[Chọn file PDF]
       │
       ▼
[PDFConverter.convert_file()]
       │
       ├─ Mở PDF với pymupdf
       ├─ Trích xuất DocMeta
       ├─ Render Markdown với pymupdf4llm
       │
       ▼
[MarkdownPostProcessor.process()]
       │
       ├─ TextCleaner (Unicode, dehyphenate, headers/footers…)
       ├─ Xử lý bảng → placeholder
       ├─ Chuẩn hóa heading
       ├─ Xử lý ngắt trang
       ├─ Xóa số trang
       ├─ In đậm từ khóa
       └─ Thêm DocMeta
       │
       ▼
[AIProcessor.process()] ← (nếu bật AI)
       │
       ▼
[Ghi file .md ra đĩa]
```

---

## Công nghệ sử dụng

| Thư viện | Phiên bản | Vai trò |
|---|---|---|
| [Flet](https://flet.dev/) | ≥ 0.80.0 | Framework giao diện desktop (Flutter-based) |
| [PyMuPDF](https://pymupdf.readthedocs.io/) | ≥ 1.25.0 | Đọc và xử lý file PDF |
| [pymupdf4llm](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) | ≥ 0.0.17 | Chuyển đổi PDF → Markdown tối ưu cho LLM |
| [LiteLLM](https://docs.litellm.ai/) | ≥ 1.0.0 | Giao tiếp thống nhất với nhiều AI provider |
| [PyInstaller](https://pyinstaller.org/) | *(tùy chọn)* | Đóng gói thành file EXE độc lập |

---

## Giấy phép

Dự án được phát hành theo giấy phép [MIT](LICENSE).
