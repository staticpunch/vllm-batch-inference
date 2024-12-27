question_template = """
Dựa vào đoạn văn bản sau:

{{text}}

Hãy tạo ra 4 câu hỏi có thể trả lời được bằng thông tin trong đoạn văn trên, với độ khó tăng dần.

1. **Câu hỏi dễ:**  Một câu hỏi tìm kiếm thông tin trực tiếp và rõ ràng được nêu trong đoạn văn. Câu trả lời có thể được tìm thấy dễ dàng bằng cách đọc lướt qua.

2. **Câu hỏi trung bình:** Một câu hỏi yêu cầu hiểu và tổng hợp một vài thông tin hoặc chi tiết liên quan trong đoạn văn. Câu trả lời đòi hỏi phải đọc kỹ hơn và kết nối các phần khác nhau.

3. **Câu hỏi khó:** Một câu hỏi đòi hỏi suy luận hoặc rút ra kết luận dựa trên thông tin trong đoạn văn. Câu trả lời không được nêu trực tiếp mà cần phải suy nghĩ và phân tích.

4. **Câu hỏi rất khó:** Một câu hỏi phức tạp, có thể yêu cầu so sánh, đối chiếu, đánh giá, hoặc áp dụng thông tin từ đoạn văn vào một bối cảnh mới (vẫn dựa trên thông tin trong văn bản). Câu trả lời có thể có nhiều cách diễn đạt và đòi hỏi sự hiểu biết sâu sắc về nội dung.

Các câu hỏi nên đa dạng về loại (ví dụ: ai, cái gì, khi nào, ở đâu, tại sao, như thế nào). **Các câu hỏi phải bằng tiếng Việt và không bắt đầu bằng những cụm từ như "Theo văn bản", "Căn cứ vào nội dung", hoặc các cụm từ giới thiệu tương tự.** Chỉ sử dụng thông tin trong đoạn văn để đặt câu hỏi.

Yêu cầu định dạng output:

Danh sách câu hỏi phải được đặt trong cặp thẻ <QUESTIONS> và </QUESTIONS>. Mỗi câu hỏi được đánh số thứ tự từ 1 đến 4, không cần ghi chú thêm độ khó (dễ, trung bình, khó, rất khó). Ví dụ:

```
<QUESTIONS>
1. Câu hỏi 1
2. Câu hỏi 2
3. Câu hỏi 3
4. Câu hỏi 4
</QUESTIONS>
```

**Lưu ý quan trọng:** Phản hồi của bạn chỉ chứa danh sách câu hỏi theo định dạng được hướng dẫn bên trên, được bao bọc bởi thẻ `<QUESTIONS>` và `</QUESTIONS>`. Không thêm bất kỳ câu trả lời, lời giải thích hoặc thông tin bổ sung nào khác.
""".strip()
