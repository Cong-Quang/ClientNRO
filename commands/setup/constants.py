"""
Hằng số game dùng chung cho setup accounts.
Bao gồm: ID NPC, ID map, ID item, cấu hình upgrade, giftcode, v.v.
"""

# ── Các bước (Step IDs) ──────────────────────

STEP_CREATE_CHAR = 1       # Tạo nhân vật mới
STEP_SELECT_CHAR = 2       # Chọn nhân vật (vào game)
STEP_GO_HOME = 3           # Di chuyển về nhà
STEP_OPEN_MURI = 4         # Mở NPC Ông Muri
STEP_CLAIM_REWARDS = 5     # Nhận thưởng (vàng/ngọc/giftcode/đệ tử)
STEP_FARM_BEANS = 6        # Farm đậu thần
STEP_BUY_BUA = 7           # Mua bùa tại Bà Hạt Mít
STEP_SANTA_SHOP = 8        # Mua item tại Santa shop
STEP_USE_SUPPORT = 9       # Dùng item hỗ trợ (1182 → 441, 1680)
STEP_ACTIVATE_ITEMS = 10   # Kích hoạt vật phẩm thưởng
STEP_UPGRADE_16 = 11       # Ép sao Item 16 (x11)
STEP_UPGRADE_OTHER = 12    # Ép sao Item 1/22/28/12
STEP_EQUIP_MASTER = 13     # Mặc đồ cho sư phụ
STEP_EQUIP_PET = 14        # Mặc đồ cho đệ tử

ALL_STEPS = [
    STEP_CREATE_CHAR, STEP_SELECT_CHAR, STEP_GO_HOME, STEP_OPEN_MURI,
    STEP_CLAIM_REWARDS, STEP_FARM_BEANS, STEP_BUY_BUA, STEP_SANTA_SHOP,
    STEP_USE_SUPPORT, STEP_ACTIVATE_ITEMS,
    STEP_UPGRADE_16, STEP_UPGRADE_OTHER,
    STEP_EQUIP_MASTER, STEP_EQUIP_PET,
]

# Server MAX_STAR = 10 (EpSaoTrangBi.MAX_STAR)
# Mỗi star Item 16 cho +3% sức đánh (option 50 param=3), 10 stars = 30% sức đánh
UPGRADE_TIMES_PER_PIECE = 10

STEP_LABELS = {
    STEP_CREATE_CHAR: "Tạo nhân vật",
    STEP_SELECT_CHAR: "Chọn nhân vật",
    STEP_GO_HOME: "Về nhà",
    STEP_OPEN_MURI: "Mở NPC Muri",
    STEP_CLAIM_REWARDS: "Nhận thưởng (vàng/ngọc/giftcode/đệ tử)",
    STEP_FARM_BEANS: "Farm đậu thần",
    STEP_BUY_BUA: "Mua bùa",
    STEP_SANTA_SHOP: "Santa shop",
    STEP_USE_SUPPORT: "Dùng item hỗ trợ",
    STEP_ACTIVATE_ITEMS: "Kích hoạt vật phẩm thưởng",
    STEP_UPGRADE_16: "Ép sao Item 16 (x11)",
    STEP_UPGRADE_OTHER: "Ép sao Item 1/22/28/12",
    STEP_EQUIP_MASTER: "Mặc đồ cho sư phụ",
    STEP_EQUIP_PET: "Mặc đồ cho đệ tử",
}

# ── Giới tính nhân vật ───────────────────────

GENDER_TRAI_DAT = 0        # Trái Đất
GENDER_NAMEK = 1           # Namek
GENDER_XAYDA = 2           # Xayda

# ── Map nhà theo giới tính ───────────────────

HOME_MAPS = {GENDER_TRAI_DAT: 21, GENDER_NAMEK: 22, GENDER_XAYDA: 23}
HOME_NPC = {GENDER_TRAI_DAT: 0, GENDER_NAMEK: 2, GENDER_XAYDA: 1}

# ── Map Santa theo giới tính ─────────────────

SANTA_MAPS = {GENDER_TRAI_DAT: 5, GENDER_NAMEK: 13, GENDER_XAYDA: 20}

# ── Kiểu tóc mặc định theo giới tính ─────────

HAIR_BY_GENDER = {GENDER_TRAI_DAT: 64, GENDER_NAMEK: 9, GENDER_XAYDA: 6}

# ── NPC IDs ──────────────────────────────────

NPC_SANTA = 39              # NPC Santa (Đảo Kame / map home)
NPC_DAU_THAN = 4            # NPC đậu thần (trong nhà)
NPC_BA_HAT_MIT = 21         # NPC Bà Hạt Mít (ép sao, mua bùa)

# ── Map IDs ──────────────────────────────────

MAP_VACH_NUI = 43           # Vách Núi Moori (mua bùa)
MAP_DAO_KAME = 5            # Đảo Kame (NPC Bà Hạt Mít - ép sao)

# ── Đậu thần ─────────────────────────────────

BEAN_ITEM_IDS = [13, 60, 61, 62, 63, 64, 65, 352, 523, 595]
TARGET_BEAN_QTY = 1000      # Số đậu thần cần farm

# ── Giftcode ─────────────────────────────────

GIFTCODES = ["tdstudio"]

# ── Bùa (1 tháng) ───────────────────────────

BUA_ITEM_IDS = [213, 214, 215, 216, 217, 218, 219, 522, 671, 672]

# ── Santa shop items ─────────────────────────

SANTA_ITEM_HO_TRO = [
    (517, 100), (518, 50),  # Các item hỗ trợ cơ bản
    (402, 20), (403, 20)   # Sách kĩ năng đệ tử (nằm trong Cửa hàng Hỗ trợ)
]
SANTA_ITEM_USE = [(402, 6), (403, 6)]              # Dùng 6 lần mỗi item sau khi mua
SANTA_NO_BAG_ITEMS = {517, 518}          # Items không vào balo (bay, pet, sách...)

# ── Item hỗ trợ ──────────────────────────────

ITEM_1182 = 1182            # Dùng để nhận item 441
ITEM_441 = 441              # Mục tiêu: >= 20
ITEM_1680 = 1680            # Dùng 1 lần

# ── Item kích hoạt thưởng ────────────────────

ACTIVATE_ITEMS_ONCE = [290, 1269, 1357, 1649, 1983, 1499, 1323]
ITEM_2000 = 2000
ITEM_2000_USE_TIMES = 2

# ── Upgrade / Ép sao ─────────────────────────

# Trang bị: items cần ép (mỗi set gồm 5 món)
ITEM_EQUIP = [1, 7, 22, 28, 12]
ITEM_7 = 7

# Nguyên liệu
ITEM_UPGRADE_16 = 16            # Nguyên liệu chính (ép cho từng trang bị)
ITEM_UPGRADE_16_CRYSTAL = 1     # Item 1 = nguyên liệu pha lê (dùng ép Item 16)
ITEM_UPGRADE_16_TIMES = 10      # Số lần ép Item 16 tối đa
ITEM_12 = 12
ITEM_442 = 442                  # Nguyên liệu đặc biệt cho Item 12 set 2

# Set Liên Hoàn (mỗi set gồm 5 trang bị)
SET_LIEN_HOAN_ITEMS = [1, 7, 22, 28, 12]
SETS_NEEDED = 2

# Tab combine (server-side)
EP_SAO_TRANG_BI = 500

# ── Cấu hình retry cho mỗi bước ──────────────

from services.retry import RetryConfig

RETRY_CONFIGS = {
    STEP_CREATE_CHAR:    RetryConfig(2, 0.5, 2.0, 1.0),
    STEP_SELECT_CHAR:    RetryConfig(3, 0.5, 3.0, 1.0),
    STEP_GO_HOME:        RetryConfig(3, 0.5, 3.0, 1.0),
    STEP_OPEN_MURI:      RetryConfig(3, 0.3, 2.0, 1.0),
    STEP_CLAIM_REWARDS:  RetryConfig(3, 0.3, 2.0, 1.0),
    STEP_FARM_BEANS:     RetryConfig(3, 0.5, 3.0, 1.0),
    STEP_BUY_BUA:        RetryConfig(2, 0.5, 3.0, 1.0),
    STEP_SANTA_SHOP:     RetryConfig(2, 0.5, 3.0, 1.0),
    STEP_USE_SUPPORT:    RetryConfig(2, 0.3, 2.0, 1.0),
    STEP_ACTIVATE_ITEMS: RetryConfig(2, 0.3, 2.0, 1.0),
    STEP_UPGRADE_16:     RetryConfig(3, 0.5, 3.0, 1.0),
    STEP_UPGRADE_OTHER:  RetryConfig(3, 0.5, 3.0, 1.0),
    STEP_EQUIP_MASTER:   RetryConfig(2, 0.3, 2.0, 1.0),
    STEP_EQUIP_PET:      RetryConfig(2, 0.3, 2.0, 1.0),
}
