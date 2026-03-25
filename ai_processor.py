import os
import time
import litellm
from typing import Optional

PROMPTS = {
    "Tóm tắt": "Bạn là một trợ lý ảo tổng hợp thông tin. Dưới đây là nội dung văn bản. Hãy tóm tắt lại các ý chính một cách ngắn gọn, súc tích và dễ hiểu:\n\n{text}",
    "Dịch sang Tiếng Việt": "Bạn là một biên dịch viên chuyên nghiệp. Dưới đây là nội dung văn bản gốc. Hãy dịch toàn bộ nội dung này sang Tiếng Việt một cách trôi chảy, tự nhiên và chính xác. Đảm bảo giữ nguyên cấu trúc định dạng Markdown (nếu có):\n\n{text}",
    "Sửa lỗi OCR (Proofread)": "Bạn là một biên tập viên chuyên nghiệp. Đoạn văn bản dưới đây được kết xuất từ file PDF/Ảnh thông qua công nghệ OCR nên có thể chứa nhiều lỗi chính tả, lỗi nhận dạng ký tự, hoặc ngắt dòng sai. Hãy sửa lại các lỗi này để văn bản hoàn hảo nhất có thể, giữ nguyên ngôn ngữ gốc và cấu trúc định dạng Markdown chuẩn:\n\n{text}",
    "Tối ưu hóa cho RAG (Làm sạch Markdown)": "Bạn là một chuyên gia chuẩn bị dữ liệu (Data Preprocessor) cho hệ thống trí tuệ nhân tạo. Nhiệm vụ của bạn là tối ưu hóa đoạn văn bản Markdown (được trích xuất từ tài liệu cấu trúc phức tạp) để phục vụ tốt nhất cho các hệ thống RAG (Retrieval-Augmented Generation) và AI.\n\nYêu cầu:\n1. Gỡ bỏ triệt để các header/footer thừa, dấu trang, số trang, số dòng lặp lại của bản in.\n2. Chuẩn hóa các Heading (H1, H2, H3), độ thụt lề, khoảng trắng dư thừa sao cho thống nhất.\n3. Sửa các từ bị đứt quãng do ngắt dòng (word-wrap) và các lỗi nhận dạng ký tự (OCR) cơ bản mà không làm thay đổi ngữ nghĩa gốc.\n4. Giữ nguyên TOÀN BỘ cấu trúc bảng biểu, blockquote, đoạn code, liên kết và danh sách.\n5. Xóa bỏ các ký tự rác không hợp lệ, emoji không cần thiết xuất hiện ngẫu nhiên.\n6. CHỈ CHẢ VỀ MÃ MARKDOWN ĐÃ ĐƯỢC LÀM SẠCH VÀ TỐI ƯU HÓA, TUYỆT ĐỐI KHÔNG TỰ Ý THÊM VÀO LỜI GIẢI THÍCH, NHẬN XÉT HAY KẾT LUẬN NÀO BÊN NGOÀI NỘI DUNG VĂN BẢN.\n\nDữ liệu đầu vào cần làm sạch:\n\n{text}"
}

MODELS_MAPPING = {
    "ChatGPT (gpt-4o-mini) - Tối ưu nhất": {"name": "gpt-4o-mini", "env": "OPENAI_API_KEY", "provider": "ChatGPT"},
    "Gemini (1.5-flash) - Tốt cho file dài": {"name": "gemini/gemini-1.5-flash", "env": "GEMINI_API_KEY", "provider": "Gemini"},
    "NVIDIA (Llama3-70b) - Tốc độ cao": {"name": "nvidia_nim/meta/llama3-70b-instruct", "env": "NVIDIA_NIM_API_KEY", "provider": "NVIDIA"}
}

class AIProcessor:
    def __init__(self, provider: str, api_key: str, task: str):
        self.provider = provider
        self.api_key = api_key.strip()
        self.task = task
        
    def _chunk_text(self, text: str, max_chars: int = 12000) -> list[str]:
        """Chia văn bản thành các đoạn nhỏ dựa trên dấu ngắt đoạn, không vượt quá max_chars."""
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = []
        current_length = 0
        
        for p in paragraphs:
            p_len = len(p)
            if current_length + p_len + 2 > max_chars and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [p]
                current_length = p_len
            else:
                current_chunk.append(p)
                current_length += p_len + 2
                
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
        return chunks

    def process(self, text: str, log_callback=None) -> str:
        """Xử lý văn bản đầu vào thông qua model AI đã chọn. Chứa cơ chế chia nhỏ (chunk) nếu quá dài."""
        if not text.strip():
            return text
            
        if self.provider not in MODELS_MAPPING:
            raise ValueError(f"AI Provider '{self.provider}' không hợp lệ hoặc chưa được hỗ trợ.")
            
        model_info = MODELS_MAPPING[self.provider]
        
        if not self.api_key:
            raise ValueError(f"Vui lòng nhập API Key cho {model_info['provider']}.")
            
        model_name = model_info["name"]
        env_key = model_info["env"]
        
        # Thiết lập biến môi trường tạm thời cho litellm
        os.environ[env_key] = self.api_key
        
        # Lấy template prompt tương ứng với task
        prompt_template = PROMPTS.get(self.task, PROMPTS["Tóm tắt"])
        
        # Chia nhỏ text
        chunks = self._chunk_text(text, max_chars=15000)
        results = []
        
        if log_callback and len(chunks) > 1:
            log_callback(f"   🤖 Văn bản khá dài, đã chia thành {len(chunks)} đoạn (chunks)...")
        
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            prompt = prompt_template.format(text=chunk)
            
            if log_callback:
                log_callback(f"   🤖 Đang xử lý chunk {idx+1}/{len(chunks)} ...")
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = litellm.completion(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    res_text = response.choices[0].message.content or ""
                    results.append(res_text.strip())
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        if log_callback:
                            log_callback(f"   ⚠️ Lỗi chunk {idx+1} (Thử lại {attempt+1}/{max_retries-1}): {str(e)}")
                        time.sleep(2 ** attempt)
                    else:
                        raise Exception(f"Lỗi AI ({self.provider}) ở chunk {idx+1}/{len(chunks)} sau {max_retries} lần thử: {str(e)}")
                
        return "\n\n".join(results)
