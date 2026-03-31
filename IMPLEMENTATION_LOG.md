# IMPLEMENTATION LOG — KidCoin Project

> Đây là bộ nhớ trung tâm của dự án theo cơ chế journaling quy định tại `PROJECT.cursorrules`.
> Mỗi entry được ghi theo thứ tự thời gian tăng dần. Nội dung **cuối cùng là mới nhất**.

---

## [2026-03-27] ENTRY #1 — Onboarding & Family Profile Management

### Task vừa hoàn thành
- Thay thế hardcoded credentials ("Bố Tuấn", "1234") bằng luồng onboarding thực sự.
- Bố mẹ có thể tự đăng ký Family Profile (tên, địa chỉ, thông tin bổ sung).
- Thêm giao diện quản lý/cập nhật thông tin gia đình từ Parent Dashboard.

### Files đã thay đổi
- `app/models/user_family.py` — Thêm trường `address`, `extra_info` vào model `Family`.
- `app/api/v1/parent.py` — Thêm endpoint `PUT /family` để update profile.
- `app/templates/parent_dashboard.html` — Thêm modal "Chỉnh sửa thông tin Nhà".

### Conventions đã áp dụng
- Soft-delete pattern: `is_deleted = False` trên model.
- Response model dùng Pydantic `BaseModel` với `from_attributes = True`.

### Bước tiếp theo (Pending)
- Implement notification navigation khi click vào thông báo.

---

## [2026-03-27] ENTRY #2 — Notification Navigation & Club Approval Flow

### Task vừa hoàn thành
- Fix `handleNotificationClick` (parent) và `handleKidNotificationClick` (kid).
- Click vào notification giờ tự navigate đến đúng tab và hiện đúng modal.
- Hỗ trợ `action_data.show_club_approve_modal` để hiển thị modal duyệt tham gia club.
- Kid nhận notification khi task được duyệt/từ chối — hiện modal khen/phê bình.

### Files đã thay đổi
- `app/templates/parent_dashboard.html` — Cập nhật `handleNotificationClick`.
- `app/templates/kid_dashboard.html` — Cập nhật `handleKidNotificationClick`, thêm Praise Modal.

### Bước tiếp theo (Pending)
- Triển khai Reward Suggestions từ Master Database.

---

## [2026-03-29] ENTRY #3 — Master Task Suggestions & Self-Selection

### Task vừa hoàn thành
- Kid có thể xem danh sách gợi ý việc làm từ Master Task DB.
- Bấm "LÀM NGAY" → tự động thêm task vào FamilyTask (endpoint `POST /quests/pick-master`).
- Giao diện dạng horizontal scroll card cho danh sách gợi ý.
- Thêm search bar cho màn hình gợi ý việc của bé.

### Files đã thay đổi
- `app/api/v1/quests.py` — Thêm `GET /quests/master`, `POST /quests/pick-master`.
- `app/schemas/quest.py` — Thêm `QuestBase` (có `min_age`, `max_age`), `QuestProposeRequest`.
- `app/models/tasks_rewards.py` — Thêm `min_age`, `max_age` vào `MasterTask`.
- `app/templates/kid_dashboard.html` — Thêm section gợi ý, search bar, hàm `pickTask`.

### Bug tìm thấy & xử lý
- `propose_master_task` bị thiếu route decorator `@router.post` → **hàm không hoạt động**.
  - Trạng thái: **Còn tồn tại trong code, cần fix**.

### Bước tiếp theo (Pending)
- Triển khai tính năng tương tự cho Reward (Gợi ý quà).

---

## [2026-03-30] ENTRY #4 — Reward Discovery System (Master Rewards)

### Task vừa hoàn thành
- Thêm `min_age`, `max_age` vào model `MasterReward`.
- Kid có thể xem gợi ý quà từ Master Reward DB với tìm kiếm & sắp xếp theo độ tuổi.
- Kid bấm "XIN QUÀ" → gửi notification tới phụ huynh (endpoint `POST /rewards/propose-master`).
- Parent Dashboard: Thêm search bar trong modal "Thêm quà" để lọc Master Reward suggestions.
- Backend: `GET /api/v1/rewards/master` (cho Kid) và `GET /api/v1/parent/master-rewards` (cho Parent).

### Files đã thay đổi
- `app/models/tasks_rewards.py` — Thêm `min_age`, `max_age` vào `MasterReward`.
- `app/api/v1/rewards.py` — Thêm `GET /master` và `POST /propose-master`.
- `app/api/v1/parent.py` — Update `GET /master-rewards` hỗ trợ query `q=...`.
- `app/schemas/reward.py` — Thêm `MasterRewardResponse`, `RewardProposeRequest`.
- `app/templates/kid_dashboard.html` — Thêm section "Gợi ý quà tặng ✨", search bar, `proposeReward`.
- `app/templates/parent_dashboard.html` — Thêm search input trong reward modal, `filterRewardSuggestions`.

### Bước tiếp theo (Pending)
- **[BUG - CRITICAL]** Restore hàm `loadPending()` bị mất trong `parent_dashboard.html` — Tab "Chờ duyệt" không hoạt động.
- Xem xét các vấn đề logic & UX đã note trong mục REVIEW bên dưới.

---

## [2026-03-30] ENTRY #5 — Code Review: Phân tích Logic & UX Issues

> Review toàn bộ codebase hiện tại. Các vấn đề được phân loại theo mức độ.
> **Chưa apply bất kỳ thay đổi nào.** Chờ xác nhận của bạn.

---

### 🔴 BUG NGHIÊM TRỌNG (Cần fix ngay)

#### BUG-01: `loadPending` bị mất — Tab "Chờ duyệt" bị hỏng hoàn toàn
- **File:** `parent_dashboard.html`
- **Vấn đề:** Hàm `loadPending()` được gọi ở 3 nơi (dòng 1059, 1603, 1620) nhưng **không có định nghĩa** trong file. `switchTab('pending')` sẽ throw `ReferenceError: loadPending is not defined`.
- **Root cause:** Hàm bị xóa nhầm trong một lần sửa code trước đó.
- **Đề xuất fix:** Thêm lại hàm `async function loadPending()` fetching từ `/parent/pending-tasks` và `/parent/pending-redemptions`, render vào `#pending-tasks-full` và `#pending-rewards-full`.

#### BUG-02: `propose_master_task` trong `quests.py` thiếu route decorator
- **File:** `app/api/v1/quests.py`, dòng 408
- **Vấn đề:** Hàm `async def propose_master_task(...)` không có `@router.post(...)` phía trên → **endpoint này không tồn tại**, không thể gọi được.
- **Đề xuất fix:** Thêm `@router.post("/propose-master", response_model=dict)` trước hàm này (hiện tại chức năng propose task đang dùng `pick-master` thay thế, cần làm rõ vai trò hai hàm).

---

### 🟡 VẤN ĐỀ LOGIC (Nên xem xét)

#### LOGIC-01: Approval endpoint bị nhân đôi — Hai luồng duyệt task song song
- **Files:** `app/api/v1/quests.py` (endpoint `POST /{log_id}/verify`) và `app/api/v1/parent.py` (endpoint `POST /tasks/{log_id}/approve`)
- **Vấn đề:** Có **hai endpoint riêng biệt** để duyệt task. `quests.py#verify_quest` không gửi notification cho kid khi REJECT (thiếu notify). `parent.py#approve_task` không gửi notification cho kid khi APPROVE hoặc REJECT. Frontend Parent Dashboard đang dùng `parent.py#approve_task` — Kid sẽ **không nhận được notification** sau khi task được duyệt từ tab Pending.
- **Đề xuất:** Hợp nhất về một endpoint duy nhất hoặc bổ sung notification vào `parent.py#approve_task`.

#### LOGIC-02: Xử lý pending task không phân biệt Family Task vs Club Task
- **File:** `app/api/v1/parent.py`, hàm `get_pending_tasks` (dòng 162)
- **Vấn đề:** Query chỉ join `FamilyTask` (`TaskLog.family_task_id == FamilyTask.id`), bỏ qua `club_task_id`. Nếu kid nộp club task, nó sẽ **không xuất hiện trong tab Chờ duyệt**.
- **Model constraint:** `TaskLog` có `CheckConstraint("num_nonnulls(family_task_id, club_task_id) = 1")` — một log phải có EITHER family_task_id OR club_task_id. Query hiện tại chỉ cover family tasks.
- **Đề xuất:** Mở rộng query hoặc tạo query riêng cho club task logs.

#### LOGIC-03: `confirm_reward_delivery` trong `parent.py` bị nhân đôi với `deliver_reward` trong `rewards.py`
- **Files:** `parent.py` dòng 855 và `rewards.py` dòng 131
- **Vấn đề:** Cả hai endpoint đều dùng `POST/PUT /rewards/{id}/confirm` hoặc `/delivery/{id}` làm cùng chức năng. Frontend dùng `parent.py#confirm` — OK. Nhưng `rewards.py#deliver_reward` gửi notification cho kid sau khi deliver, còn `parent.py#confirm_reward_delivery` **không gửi notification cho kid**.
- **Đề xuất:** Thêm notification vào `parent.py#confirm_reward_delivery` hoặc chuyển frontend về dùng endpoint `rewards.py`.

#### LOGIC-04: Race condition trong reward stock decrement
- **File:** `app/api/v1/rewards.py`, `redeem_reward`, dòng 55 và 80
- **Vấn đề:** Kiểm tra `stock_limit <= 0` và sau đó `stock_limit -= 1` không atomic. Nếu hai kid cùng lúc redeem, cả hai đều qua check và stock có thể âm.
- **Đề xuất:** Dùng `SELECT FOR UPDATE` lock hoặc atomic `UPDATE SET stock_limit = stock_limit - 1 WHERE stock_limit > 0`.

#### LOGIC-05: `QuestItem` schema có `id` là cả `Optional[int]` (từ QuestBase) và `Optional[UUID]` override
- **File:** `app/schemas/quest.py`
- **Vấn đề:** `QuestBase.id` là `Optional[int]` (dành cho master task id), nhưng `QuestItem` kế thừa và override thành `Optional[UUID]` (log id). Điều này gây nhầm lẫn semantic — hai field cùng tên `id` mang nghĩa khác nhau tùy class.
- **Đề xuất:** Đổi tên thành `log_id: Optional[UUID]` trong `QuestItem` và `master_id: Optional[int]` trong `QuestBase`.

Fixed in 30/3/2026
---

### 🟢 VẤN ĐỀ UX / UI (Cải thiện trải nghiệm)

#### UX-01: Sau khi Kid "LÀM NGAY" một task từ gợi ý, task xuất hiện trong danh sách nhưng vẫn phải bấm "Làm xong!" thêm một lần nữa
- **Vấn đề:** Flow hiện tại là: Kid chọn task từ gợi ý → task được thêm vào FamilyTask → Kid phải quay về tab Nhiệm vụ → tìm task đó → bấm "Làm xong!". Đây là hai bước tách biệt, gây friction.
- **Đề xuất:** Sau khi pick task thành công, tự động scroll lên đầu tab Nhiệm vụ hoặc hiện prompt hỏi "Bạn đã làm xong việc này chưa?" và submit ngay.

#### UX-02: Kid bấm "XIN QUÀ" nhiều lần mà không có giới hạn — spam notification tới Parent
- **File:** `app/api/v1/rewards.py`, `propose_master_reward`
- **Vấn đề:** Mỗi lần bấm "XIN QUÀ" đều tạo notification mới cho parent, không có cooldown hoặc dedup logic. Kid có thể spam request.
- **Đề xuất:** Kiểm tra xem đã có notification pending nào với `reference_id = master.id` và `user_id = parent.id` chưa trước khi tạo mới. Hoặc thêm cooldown theo session.

#### UX-03: Notification cho Reward Proposal link đến sai tab
- **File:** `app/api/v1/rewards.py`, `propose_master_reward`, dòng 250
- **Vấn đề:** `action_data={"tab": "shop", ...}` — parent click notification sẽ được navigate tới tab "shop" nhưng tab đó là cửa hàng của kid. Parent nên được navigate tới tab "rewards" (quản lý phần thưởng) để thêm quà vào shop.
- **Đề xuất:** Đổi `"tab": "shop"` thành `"tab": "rewards"`.

#### UX-04: Danh sách quà gợi ý trong Shop tab của Kid hiển thị nhưng không refresh khi switch tab
- **File:** `kid_dashboard.html`, hàm `switchTab`, dòng 858
- **Vấn đề:** `if (tabId === 'shop') fetchRewards()` — chỉ fetch family rewards, **không fetch** `fetchMasterRewardSuggestions()`. Nếu bé vào tab Shop lần đầu tiên sau khi mở app, phần gợi ý có thể trống.
- **Đề xuất:** Thêm `fetchMasterRewardSuggestions()` khi switch sang tab shop.

#### UX-05: Không có feedback khi Parent duyệt task từ notification và navigate
- **Vấn đề:** Khi parent nhận notification task pending và click để navigate → `switchTab('pending')`, nhưng `loadPending()` hiện bị mất (BUG-01). Ngoài ra ngay cả khi fix, không có highlight/focus vào task cụ thể cần duyệt.
- **Đề xuất:** Sau khi fix BUG-01, cân nhắc scroll-to hay highlight task cụ thể có `log_id` từ `action_data`.

#### UX-06: Kid không biết trạng thái "Xin quà" sau khi gửi — không có wishlist
- **Vấn đề:** Sau khi kid bấm "XIN QUÀ", không có chỗ nào để kid xem "Mình đã xin quà gì rồi?" hoặc "Bố mẹ đã duyệt chưa?". Trạng thái ước muốn là one-way, opaque với kid.
- **Đề xuất (future):** Thêm section "Điều ước của bé 🌟" trong Shop tab, hiển thị danh sách quà đã xin và trạng thái (Đang chờ / Đã có trong shop / Chưa được duyệt).

---

### Files quan trọng cần theo dõi

| File | Vai trò | Ghi chú |
|------|---------|---------|
| `app/api/v1/parent.py` | API cho Parent | Có 2 endpoint duyệt task, cần hợp nhất |
| `app/api/v1/quests.py` | API cho Kid (Task) | `propose_master_task` thiếu decorator |
| `app/api/v1/rewards.py` | API cho Kid (Reward) | Cần dedup notification |
| `app/templates/parent_dashboard.html` | UI Parent | Thiếu `loadPending()` — critical |
| `app/templates/kid_dashboard.html` | UI Kid | switchTab shop thiếu gọi suggestions |
| `app/models/tasks_rewards.py` | DB Models | OK |
| `app/models/logs_transactions.py` | DB Models | CheckConstraint lưu ý ClubTask |

---

## [2026-03-30] ENTRY #6 — Critical Fixes & Logic Consolidation

### Task vừa hoàn thành
- **FIX BUG-01**: Khôi phục hàm `loadPending()` trong `parent_dashboard.html`. Tab "Chờ duyệt" đã hoạt động trở lại, hiển thị đầy đủ Nhiệm vụ và Quà tặng.
- **FIX BUG-02**: Thêm `@router.post("/propose-master")` cho `propose_master_task` trong `quests.py`.
- **CONSOLIDATE LOGIC**:
    - Bổ sung Notification cho Kid khi Parent duyệt/từ chối task trong `parent.py`.
    - Bổ sung Notification cho Kid khi Parent xác nhận giao quà trong `parent.py`.
- **UX IMPROVEMENTS**:
    - Sửa link notification của phần xin quà dẫn về đúng tab `rewards` (Quản lý phần thưởng) của phụ huynh.
    - Tự động load danh sách quà gợi ý khi bé chuyển sang tab Cửa hàng.

### Files đã thay đổi
- `app/templates/parent_dashboard.html` — Thêm `loadPending()`.
- `app/api/v1/quests.py` — Thêm decorator cho `propose_master_task`.
- `app/api/v1/parent.py` — Bổ sung Notification logic trong `approve_task` và `confirm_reward_delivery`.
- `app/api/v1/rewards.py` — Sửa `action_data` trong `propose_master_reward`.
- `app/templates/kid_dashboard.html` — Cập nhật `switchTab` để fetch quà gợi ý.

### Bước tiếp theo (Pending)
- Giải quyết **LOGIC-02**: Pending tasks đang bỏ qua Club Tasks.
- Giải quyết **LOGIC-04**: Race condition trong stock reward.
- Xem xét các UX improvements còn lại (Wishlist cho bé, highlight task từ notification).

---

## [2026-03-30] ENTRY #7 — Thiết kế Hệ thống: Lịch sử Nhiệm vụ & Quà tặng

> **Trạng thái: PLAN — Chưa triển khai. Chờ thực thi sau khi review.**

### 1. Phân tích nhu cầu

#### Phía Kid
| Nhu cầu | Hiện trạng | Vấn đề |
|---------|-----------|--------|
| Xem lịch sử làm việc của mình | Chỉ có "Việc hôm nay" trong tab Nhiệm vụ | Không thấy lịch sử các ngày trước |
| Xem quà đã đổi + trạng thái | Không có | Sau khi bấm "Đổi Ngay" trong Shop, không thấy gì |
| Biết quà mình "xin" đã được duyệt chưa | Không có | Bấm "XIN QUÀ" xong là mất tích |

#### Phía Parent
| Nhu cầu | Hiện trạng | Vấn đề |
|---------|-----------|--------|
| Xem tiến độ từng bé theo ngày | Card bé chỉ có Xu + XP | Không thể xem task/reward của từng bé |
| Duyệt/Giao ngay từ card bé | Không có | Phải vào tab "Chờ duyệt" riêng |
| Lịch sử 30 ngày của bé | Không có | Chỉ có Audit Log chung |

---

### 2. Thiết kế API Backend (mới cần tạo)

#### 2a. `GET /api/v1/quests/my-history` (cho Kid)
**Mục đích:** Kid xem lịch sử tất cả nhiệm vụ đã nộp của mình (không chỉ hôm nay).

```
Query params: ?limit=20&offset=0
Response schema:
[
  {
    "log_id": "uuid",
    "task_name": "Đánh răng",
    "points_reward": 10,
    "status": "APPROVED" | "PENDING_APPROVAL" | "REJECTED",
    "parent_comment": "Giỏi lắm!",
    "proof_image_url": "...",
    "submitted_at": "2026-03-30T08:00:00",
    "resolved_at": "2026-03-30T09:00:00"
  }
]
```
**File:** `app/api/v1/quests.py` — Query `TaskLog` theo `kid_id = current_user.id`, join `FamilyTask`, sort by `created_at desc`, giới hạn 30 ngày.

#### 2b. `GET /api/v1/rewards/my-history` (cho Kid)
**Mục đích:** Kid xem lịch sử quà đã đổi + trạng thái giao.

```
Query params: ?limit=20&offset=0
Response schema:
[
  {
    "redemption_id": "uuid",
    "reward_name": "Xem TV 30 phút",
    "points_cost": 50,
    "status": "PENDING_DELIVERY" | "DELIVERED",
    "redeemed_at": "2026-03-30T08:00:00",
    "delivered_at": null | "2026-03-30T10:00:00"
  }
]
```
**File:** `app/api/v1/rewards.py` — Query `RedemptionLog` theo `kid_id = current_user.id`, join `FamilyReward`, sort `created_at desc`.

#### 2c. `GET /api/v1/parent/kids/{kid_id}/task-history` (cho Parent)
**Mục đích:** Parent xem lịch sử nhiệm vụ của một bé cụ thể.

```
Query params: ?days=30&limit=50
Response schema: (giống 2a nhưng thêm kid info)
```
**File:** `app/api/v1/parent.py` — Giống `get_pending_tasks` nhưng bỏ filter status, thêm date range.

#### 2d. `GET /api/v1/parent/kids/{kid_id}/reward-history` (cho Parent)
**Mục đích:** Parent xem lịch sử quà của một bé cụ thể.

```
Query params: ?days=30&limit=50
Response schema: (giống 2b)
```
**File:** `app/api/v1/parent.py`

---

### 3. Thiết kế Giao diện Kid Dashboard

#### 3a. Tab mới: "Nhật ký 📜" (tab-history)

**Vị trí:** Thêm tab thứ 4 vào nav bar dưới cùng (cạnh "Thi Đua").
> ⚠️ Lưu ý: Nav bar hiện có 3 nút, khi thêm thứ 4 cần điều chỉnh khoảng cách (dùng `w-1/4` thay vì `w-1/3`).

**Nav bar HTML (mới):**
```html
<button onclick="switchTab('history')" id="btn-history" class="nav-btn ...">
    <span class="text-3xl mb-1">📜</span>
    <span class="text-xs font-black">Nhật Ký</span>
</button>
```

**Tab content (`tab-history`):**

```
┌─────────────────────────────────────┐
│  📜 NHẬT KÝ CỦA BÉ                 │
│                                     │
│  [Tab: Nhiệm vụ] [Tab: Quà tặng]   │  ← Toggle tabs bên trong
│  ─────────────────────────────────  │
│                                     │
│  [Nhiệm vụ tab active:]             │
│  ┌─────────────────────────────┐    │
│  │ 📚 Làm bài toán      +20xu │    │
│  │ 30/03/2026             ✅  │    │← chip xanh = APPROVED
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ 🪥 Đánh răng         +5xu  │    │
│  │ 30/03/2026       ⏳ waiting│    │← chip vàng = PENDING
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ 🛏️ Gấp chăn         +10xu  │    │
│  │ 29/03/2026             ❌  │    │← chip đỏ = REJECTED
│  │ 💬 "Con làm lại nhé!"      │    │← hiện comment nếu có
│  └─────────────────────────────┘    │
│                                     │
│  [Quà tặng tab:]                    │
│  ┌─────────────────────────────┐    │
│  │ 📺 Xem TV 30 phút    -50xu │    │
│  │ 30/03/2026     ⏳ chờ giao │    │← chip vàng
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ 🍦 Ăn kem            -80xu │    │
│  │ 28/03/2026      ✅ đã nhận │    │← chip xanh
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

**Chip trạng thái (màu sắc chuẩn):**
| Status | Màu | Text |
|--------|-----|------|
| APPROVED / DELIVERED | green-100 text-green-700 | ✅ Hoàn thành / ✅ Đã nhận |
| PENDING_APPROVAL / PENDING_DELIVERY | yellow-100 text-yellow-700 | ⏳ Chờ duyệt / ⏳ Chờ giao |
| REJECTED | red-100 text-red-700 | ❌ Bị từ chối |

---

### 4. Thiết kế Giao diện Parent — Kid Detail Drawer

#### Cách mở:
- Trong `loadKids()`, card bé có nút **"📋 Xem"** ở góc dưới phải (thêm vào sau 2 stats hiện tại).
- Click nút → gọi `openKidDetailDrawer(kid.id, kid.display_name)`.

#### Drawer HTML (thêm vào cuối body):
```
┌────────────────────────────────────────────┐
│ ← [Đóng]    Hồ sơ: Bé Bin 👶              │  ← Fixed header
│ ┌──────────────────────────────────────┐   │
│ │  [📋 Nhiệm vụ]  [🎁 Lịch sử quà]   │   │  ← Toggle tabs
│ └──────────────────────────────────────┘   │
│                                            │
│ [NHIỆM VỤ TAB - Cuộn được]                │
│                                            │
│ 📅 Hôm nay (30/03)                        │
│ ┌────────────────────────────────────┐     │
│ │ 📚 Làm bài toán                   │     │
│ │ +20 xu          ⏳ Chờ duyệt      │     │
│ │           [Duyệt ngay ✅] [❌]    │     │← action buttons
│ └────────────────────────────────────┘     │
│ ┌────────────────────────────────────┐     │
│ │ 🪥 Đánh răng                      │     │
│ │ +5 xu              ✅ Hoàn thành  │     │
│ └────────────────────────────────────┘     │
│                                            │
│ 📅 29/03                                   │
│ ┌────────────────────────────────────┐     │
│ │ 🛏️ Gấp chăn                        │     │
│ │ +10 xu              ❌ Bị từ chối │     │
│ └────────────────────────────────────┘     │
│                                            │
│ [QUÀ TẶNG TAB]                            │
│                                            │
│ ┌────────────────────────────────────┐     │
│ │ 📺 Xem TV 30 phút                  │     │
│ │ -50 xu          📦 Chờ giao       │     │
│ │              [Giao quà ngay 🎁]   │     │← action button
│ └────────────────────────────────────┘     │
└────────────────────────────────────────────┘
```

**Drawer design specs:**
- Dạng: `fixed bottom-0 left-0 right-0` slide-up từ dưới, che 75% màn hình, có `overflow-y-auto`.
- Backdrop: `fixed inset-0 bg-black/40` để đóng khi click ngoài.
- Animate: `translate-y-full → translate-y-0` với CSS transition.
- Trên mobile: full width, max-width none.
- Trên desktop: `max-w-2xl mx-auto`.
- Không dùng modal toàn màn hình để tránh mất context (có thể thấy dashboard phía sau).

**Nhóm ngày:**
- Group tasks/rewards theo ngày (`toLocaleDateString('vi-VN')`).
- Section header cho mỗi ngày: `📅 30 tháng 3, 2026`.
- Items trong ngày sort theo `created_at desc`.

**Action buttons (inline):**
- Task PENDING_APPROVAL → hiện [✅ Duyệt] [❌ Từ chối] → gọi `openApproveModal(log_id)`.
- Reward PENDING_DELIVERY → hiện [🎁 Giao quà] → gọi `confirmDelivery(redemption_id)`.
- Sau khi action → tự động refresh drawer content (không đóng drawer).

---

### 5. Schema Pydantic mới cần thêm

**File:** `app/schemas/quest.py`
```python
class TaskHistoryItem(BaseModel):
    log_id: UUID
    task_name: str
    points_reward: int
    status: TaskStatus
    parent_comment: Optional[str] = None
    proof_image_url: Optional[str] = None
    submitted_at: datetime
    resolved_at: Optional[datetime] = None
    class Config:
        from_attributes = True
```

**File:** `app/schemas/reward.py`
```python
class RedemptionHistoryItem(BaseModel):
    redemption_id: UUID
    reward_name: str
    points_cost: int
    status: RedemptionStatus
    redeemed_at: datetime
    delivered_at: Optional[datetime] = None
    class Config:
        from_attributes = True
```

---

### 6. Danh sách công việc thực thi (triển khai sau)

**Backend (ưu tiên 1):**
- [ ] Thêm schema `TaskHistoryItem` vào `app/schemas/quest.py`
- [ ] Thêm schema `RedemptionHistoryItem` vào `app/schemas/reward.py`
- [ ] Thêm `GET /quests/my-history` vào `quests.py`
- [ ] Thêm `GET /rewards/my-history` vào `rewards.py`
- [ ] Thêm `GET /parent/kids/{kid_id}/task-history` vào `parent.py`
- [ ] Thêm `GET /parent/kids/{kid_id}/reward-history` vào `parent.py`

**Frontend Kid (ưu tiên 2):**
- [ ] Thêm tab "Nhật Ký 📜" vào bottom nav (điều chỉnh `w-1/3` → `w-1/4`)
- [ ] Thêm HTML `tab-history` với inner tabs Nhiệm vụ / Quà tặng
- [ ] Thêm JS `fetchMyTaskHistory()` và `renderTaskHistory()`
- [ ] Thêm JS `fetchMyRewardHistory()` và `renderRewardHistory()`
- [ ] Cập nhật `switchTab('history')` trong `switchTab()`

**Frontend Parent (ưu tiên 3):**
- [ ] Thêm nút "📋 Xem" vào card bé trong `loadKids()`
- [ ] Thêm HTML Kid Detail Drawer (fixed bottom, slide-up)
- [ ] Thêm JS `openKidDetailDrawer(kidId, kidName)`
- [ ] Thêm JS `loadKidTaskHistory(kidId)` và `renderKidTaskHistory()`
- [ ] Thêm JS `loadKidRewardHistory(kidId)` và `renderKidRewardHistory()`
- [ ] Đảm bảo action buttons trong drawer gọi đúng `openApproveModal` / `confirmDelivery`

### 7. Ghi chú kỹ thuật

- `GET /quests/my-history` phải dùng `deps.require_role(Role.KID)` để tránh parent xem nhầm.
- `GET /parent/kids/{kid_id}/task-history` phải verify `kid.family_id == current_user.family_id` để tránh cross-family data leak.
- Drawer state cần biến `currentKidDetailId` để biết đang xem bé nào khi refresh sau action.
- Sau khi `confirmDelivery()` từ drawer → gọi `loadKidRewardHistory(currentKidDetailId)` để refresh drawer, không cần reload toàn trang.

