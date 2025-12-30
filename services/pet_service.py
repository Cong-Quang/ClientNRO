# toolsDev/services/pet_service.py
from models.pet import Pet, Item, ItemOption, Skill
from network.session import Session  # Giả định có một module session để gửi message
from protocol.message import Message  # Giả định có một module message

# ID của command để yêu cầu thông tin đệ tử
PET_INFO_CMD_ID = -107

# Biến toàn cục để lưu trữ thông tin đệ tử
# Trong một ứng dụng lớn hơn, bạn có thể quản lý cái này trong một lớp quản lý trạng thái
current_pet_info = Pet()

def request_pet_info(session: Session):
    """
    Gửi yêu cầu đến server để nhận thông tin đệ tử.
    """
    try:
        msg = Message(PET_INFO_CMD_ID)
        session.send_message(msg)
        print("Đã gửi yêu cầu xem thông tin đệ tử.")
    except Exception as e:
        print(f"Lỗi khi gửi yêu cầu thông tin đệ tử: {e}")

def handle_pet_info_response(msg: Message):
    """
    Xử lý phản hồi từ server chứa thông tin đệ tử.
    Hàm này sẽ được gọi bởi bộ điều khiển message chính khi nhận được message có ID là -107.
    """
    global current_pet_info
    try:
        action = msg.reader.read_byte()

        if action == 0:
            current_pet_info.has_pet = False
            print("Nhân vật không có đệ tử.")
            return

        if action == 1:
            current_pet_info.has_pet = True
            print("Nhân vật có đệ tử (chưa có thông tin chi tiết).")
            # Yêu cầu thông tin chi tiết nếu cần
            # request_pet_info(session) 
            return

        if action == 2:
            pet = Pet()
            pet.has_pet = True
            
            # Đọc trang bị
            pet.head_id = msg.reader.read_short()
            num_items = msg.reader.read_unsigned_byte()
            pet.items_body = [None] * num_items
            for i in range(num_items):
                template_id = msg.reader.read_short()
                if template_id == -1:
                    continue
                
                item = Item()
                item.template_id = template_id
                # Giả sử đã có hàm để lấy ItemTemplate từ id
                # item.template = ItemTemplates.get(template_id) 
                
                item.quantity = msg.reader.read_int()
                item.info = msg.reader.read_utf()
                item.content = msg.reader.read_utf()
                
                num_options = msg.reader.read_unsigned_byte()
                if num_options > 0:
                    item.options = []
                    for _ in range(num_options):
                        option_id = msg.reader.read_unsigned_byte()
                        param = msg.reader.read_unsigned_short()
                        if option_id != -1:
                            item.options.append(ItemOption(option_id, param))
                pet.items_body[i] = item

            # Đọc các chỉ số của đệ tử
            pet.hp = msg.reader.read_int3byte()
            pet.hp_full = msg.reader.read_int3byte()
            pet.mp = msg.reader.read_int3byte()
            pet.mp_full = msg.reader.read_int3byte()
            pet.damage_full = msg.reader.read_int3byte()
            pet.name = msg.reader.read_utf()
            pet.level_str = msg.reader.read_utf()
            pet.power = msg.reader.read_long()
            pet.potential = msg.reader.read_long()
            pet.status = msg.reader.read_byte()
            pet.stamina = msg.reader.read_short()
            pet.max_stamina = msg.reader.read_short()
            pet.critical_full = msg.reader.read_byte()
            pet.defence_full = msg.reader.read_short()

            # Đọc kỹ năng của đệ tử
            num_skills = msg.reader.read_byte()
            pet.skills = []
            for _ in range(num_skills):
                skill_id = msg.reader.read_short()
                skill = Skill()
                if skill_id != -1:
                    skill.skill_id = skill_id
                else:
                    skill.more_info = msg.reader.read_utf()
                pet.skills.append(skill)
            
            current_pet_info = pet
            print("Đã cập nhật thông tin đệ tử thành công.")
            display_pet_info()

    except Exception as e:
        print(f"Lỗi khi xử lý thông tin đệ tử: {e}")

def display_pet_info():
    """
    Hiển thị thông tin đệ tử đã được lưu trữ.
    """
    print("\n" + "="*40)
    print(current_pet_info)
    print("="*40 + "\n")

# --- Tích hợp vào tool ---
# 1. Trong file controller chính (ví dụ: `toolsDev/main.py`), bạn cần đăng ký `handle_pet_info_response`
#    để xử lý message có command ID là -107.
#    controller.register_handler(-107, handle_pet_info_response)

# 2. Tạo một tùy chọn trong menu của tool để người dùng có thể gọi `request_pet_info`.
#    def show_pet_info():
#        session = get_current_session() # Lấy session hiện tại
#        request_pet_info(session)

#    menu_options = {
#        "1": "Xem thông tin đệ tử",
#        ...
#    }
#    if choice == "1":
#        show_pet_info()