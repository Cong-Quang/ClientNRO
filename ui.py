# toolsDev/ui.py
from model.game_objects import Char
from logs.logger_config import logger

def get_pet_status_vietnamese(status: int) -> str:
    """
    Trả về trạng thái của đệ tử bằng tiếng Việt.
    """
    status_map = {
        0: "Đi theo",
        1: "Bảo vệ",
        2: "Tấn công",
        3: "Về nhà",
        4: "Hợp thể",
        5: "Hợp thể vĩnh viễn"
    }
    return status_map.get(status, f"Không xác định ({status})")

def display_pet_info():
    """
    Hiển thị thông tin chi tiết của đệ tử đã được lưu trong Char.my_petz().
    """
    pet = Char.my_petz()

    if not pet or not pet.have_pet:
        logger.info("Không có thông tin đệ tử hoặc chưa nhận được dữ liệu từ server.")
        return

    # Sử dụng logger để in ra console với định dạng màu
    logger.info("--- Thông Tin Đệ Tử ---")
    
    info_lines = [
        f"Tên: {pet.name}",
        f"Trạng thái: {get_pet_status_vietnamese(pet.pet_status)} (Status ID: {pet.pet_status})",
        f"HP: {pet.c_hp:,} / {pet.c_hp_full:,}",
        f"MP: {pet.c_mp:,} / {pet.c_mp_full:,}",
        f"Sức mạnh: {pet.c_power:,}",
        f"Tiềm năng: {pet.c_tiem_nang:,}",
        f"Sát thương: {pet.c_dam_full:,}",
        f"Phòng thủ: {pet.c_def_full:,}",
        f"Chí mạng: {pet.c_critical_full}%",
        f"Thể lực: {pet.c_stamina:,} / {pet.c_max_stamina:,}",
        "--- Kỹ năng ---"
    ]
    for line in info_lines:
        print(line) # In trực tiếp để không bị prefix của logger

    if pet.arr_pet_skill:
        for skill in pet.arr_pet_skill:
            if skill:
                if skill.skill_id != -1:
                    print(f"- Skill ID: {skill.skill_id}")
                else:
                    print(f"- Thông tin khác: {skill.more_info}")
    else:
        print("Không có kỹ năng.")
        
    print("--- Trang bị ---")
    if pet.arr_item_body:
        for item in pet.arr_item_body:
            if item:
                print(f"- Item ID: {item.item_id} (Số lượng: {item.quantity})")
                for opt in item.item_option:
                    print(f"  + Option ID: {opt.option_template_id}, Param: {opt.param}")
    else:
        print("Không có trang bị.")
    
    logger.info("--- Kết thúc ---")

def display_help():
    """Hiển thị các lệnh có sẵn."""
    logger.info("--- Trợ giúp ---")
    print("Các lệnh có sẵn:")
    print("  pet   - Hiển thị thông tin chi tiết của đệ tử.")
    print("  help  - Hiển thị bảng trợ giúp này.")
    print("  exit  - Thoát khỏi công cụ.")
    logger.info("--- Kết thúc ---")
