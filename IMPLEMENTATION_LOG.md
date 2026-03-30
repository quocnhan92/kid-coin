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
