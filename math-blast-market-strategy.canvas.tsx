import {
  BarChart,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  PieChart,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

export default function MathBlastMarketStrategy() {
  return (
    <Stack gap={28}>
      {/* ---------- HERO ---------- */}
      <Stack gap={8}>
        <H1>Math Blast — Phân tích thị trường & chiến lược sản phẩm VN</H1>
        <Text tone="secondary">
          Đánh giá khả năng tách 3 chế độ (Candy / Flappy / Arcade) thành các SKU độc lập, phân khúc
          khách hàng, sứ mệnh sản phẩm và lộ trình go-to-market cho thị trường tiểu học Việt Nam
          (Lớp 1–5, CT GDPT 2018).
        </Text>
      </Stack>

      <Grid columns={5} gap={12}>
        <Stat value="~9 triệu" label="Học sinh tiểu học VN (Lớp 1–5)" />
        <Stat value="~$3 tỷ" label="Quy mô EdTech K-12 VN 2024" />
        <Stat value="12,3% / năm" label="CAGR thị trường EdTech 2025–34" />
        <Stat value="1,05 triệu" label="HS tham gia ViOlympic 2025–26" tone="info" />
        <Stat value="15 triệu" label="Người dùng Monkey (benchmark)" tone="warning" />
      </Grid>

      <Callout
        tone="success"
        title="Kết luận sớm — không nên tách thành 3 app rời rạc"
      >
        <Text>
          Giữ <Text weight="semibold">một engine + một thương hiệu “Math Blast”</Text> nhưng đóng
          gói thành <Text weight="semibold">3 SKU độc lập về kênh phân phối & mô hình thu</Text>:{" "}
          <Text weight="semibold">Flappy</Text> (free + ads, kênh viral mua user),{" "}
          <Text weight="semibold">Candy 300</Text> (subscription B2C cho phụ huynh, lõi giữ chân &
          doanh thu),{" "}
          <Text weight="semibold">Arcade Class</Text> (B2B/B2T cho giáo viên & trung tâm). Mỗi SKU
          chia sẻ <Text>skill_id</Text>, mastery, account và content pack — chi phí nội dung trả
          một lần, phục vụ 3 nhu cầu thị trường khác nhau.
        </Text>
      </Callout>

      {/* ---------- 1. BỐI CẢNH THỊ TRƯỜNG ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>1. Bối cảnh thị trường EdTech tiểu học VN (2026)</H2>

        <Grid columns={2} gap={16}>
          <Card>
            <CardHeader>Cơ cấu chi tiêu EdTech VN 2024 (theo phân khúc)</CardHeader>
            <CardBody>
              <PieChart
                donut
                data={[
                  { label: "Pre-K & K-12 (mầm non + phổ thông)", value: 81.5, tone: "info" },
                  { label: "Đại học & sau ĐH", value: 11.5 },
                  { label: "Học tiếng Anh & kỹ năng", value: 7.0, tone: "neutral" },
                ]}
              />
              <Text tone="tertiary" size="small">
                Nguồn: GlobalData VN EdTech 2024 · K-12 chiếm $2,97 tỷ / $3,64 tỷ tổng.
              </Text>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>Chi “học thêm” Toán của phụ huynh (VND / buổi)</CardHeader>
            <CardBody>
              <BarChart
                categories={[
                  "Gia sư tại nhà (cấp 1)",
                  "Trung tâm phổ thông",
                  "Trung tâm cao cấp",
                  "Tiền tiểu học VIP",
                  "App học toán subscription",
                ]}
                series={[
                  {
                    name: "VND / buổi",
                    data: [120, 150, 250, 500, 25],
                  },
                ]}
                valueSuffix="K"
              />
              <Text tone="tertiary" size="small">
                Nguồn: tổng hợp Thanh Niên, VTC News, Gia Sư Sư Phạm 2025–26. App ~25K/buổi =
                300K/tháng quy đổi từ gói năm.
              </Text>
            </CardBody>
          </Card>
        </Grid>

        <Grid columns={3} gap={12}>
          <Card>
            <CardHeader>Động lực thuận lợi</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text>
                  • CT GDPT 2018 còn “mới” → phụ huynh lo lắng tìm công cụ luyện theo chuẩn.
                </Text>
                <Text>
                  • Smartphone phổ cập &gt;80%; trẻ tiếp cận device sớm, parent-controlled time là
                  norm.
                </Text>
                <Text>
                  • Văn hoá thi cử: ViOlympic, Toán Quốc tế (Kangaroo, IMC) — phụ huynh sẵn sàng chi.
                </Text>
                <Text>
                  • Chuyển đổi số giáo dục là chính sách quốc gia → trường công mở cửa cho app.
                </Text>
              </Stack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>Áp lực & rào cản</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text>
                  • Monkey, OLM, Edupia, ELSA đã chiếm “top of mind” phụ huynh đô thị.
                </Text>
                <Text>
                  • Phụ huynh khó tin “game = học” — cần bằng chứng tiến bộ rõ ràng.
                </Text>
                <Text>
                  • Quy định mới về dạy thêm 2025 + lo ngại screen time đẩy phụ huynh cẩn trọng hơn.
                </Text>
                <Text>
                  • Lợi nhuận ads/IAP cho trẻ &lt;13 bị COPPA & các quy định nội địa siết chặt.
                </Text>
              </Stack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>Khoảng trống thị trường</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text>
                  • Sản phẩm “Toán đơn môn, bám CT GDPT 2018, free-to-try, có leaderboard family”
                  còn ít. Monkey nặng tiếng Anh + mầm non.
                </Text>
                <Text>
                  • Công cụ <Text weight="semibold">giáo viên Tiểu học tự tạo bài tập 1 phút</Text>{" "}
                  hầu như chưa có sản phẩm VN hoá tốt.
                </Text>
                <Text>
                  • Phân khúc 6–8 tuổi <Text weight="semibold">không biết đọc nhanh</Text> — cần
                  TTS bài Toán, đa số app coi nhẹ.
                </Text>
              </Stack>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      {/* ---------- 2. TÁCH HAY KHÔNG TÁCH ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>2. Có nên tách 3 chế độ thành 3 game độc lập?</H2>
        <Text tone="secondary">
          So sánh ba phương án triển khai. Ưu tiên đánh giá: chi phí nội dung, tốc độ ra mắt, hiệu
          quả mua user, khả năng đa dạng hoá doanh thu, độ chịu rủi ro của team nhỏ.
        </Text>

        <Table
          headers={[
            "Tiêu chí",
            "PA1 · 1 app duy nhất 3 mode",
            "PA2 · 3 app hoàn toàn tách rời",
            "PA3 · 1 engine + 3 SKU (đề xuất)",
          ]}
          rows={[
            [
              "Chi phí phát triển ban đầu",
              "Thấp (1 codebase, 1 backend)",
              "Cao 2,3–2,8× (3 storefront, 3 UA funnel)",
              "Thấp–TB (1 core + 3 shell client)",
            ],
            [
              "Chi phí nội dung (300 màn + pool kỹ năng)",
              "1× (dùng chung)",
              "3× nếu không tái sử dụng manifest",
              "1× (content pack chung, §5.A.7 & §5.B.15)",
            ],
            [
              "Tốc độ ra MVP",
              "Nhanh (đã có v1)",
              "Chậm — 3 lần phê duyệt store, 3 ASO",
              "Nhanh — Flappy trước, Candy nối, Arcade sau",
            ],
            [
              "Khả năng mua user (CAC)",
              "Mức TB — phải bán “3-in-1” khó định vị",
              "Cao — mỗi app có thị trường riêng nhưng phải xây 3 brand",
              "Thấp nhất — Flappy = hook viral free, Candy = retention paid",
            ],
            [
              "Đa dạng mô hình doanh thu",
              "Khó kết hợp ads + subscription trong 1 app cho trẻ <13",
              "Dễ tách: app ads / app subscription / app B2B",
              "Tách rõ — mỗi SKU 1 model, không xung đột chính sách store",
            ],
            [
              "Vận hành (DevOps, support)",
              "Đơn giản nhất",
              "Phức tạp gấp 3",
              "Trung bình — 1 backend, 3 binary",
            ],
            [
              "Đo lường & học dữ liệu chéo (cross-mode mastery §5.B.13)",
              "Tự động OK",
              "Phải xây bridge phức tạp",
              "OK — chia sẻ skill_id, mastery, account",
            ],
            [
              "Rủi ro thương hiệu (1 SKU sự cố kéo các SKU khác)",
              "Cao — 1 review xấu kéo toàn bộ",
              "Thấp — cô lập",
              "Trung bình — brand chung nhưng SKU độc lập trên store",
            ],
            [
              "Phù hợp team nhỏ (<5 dev)",
              "Tốt",
              "Quá tải",
              "Tốt nhất, đi từng giai đoạn",
            ],
          ]}
          rowTone={[
            undefined,
            undefined,
            undefined,
            undefined,
            "info",
            undefined,
            undefined,
            undefined,
            "success",
          ]}
          columnAlign={["left", "left", "left", "left"]}
        />

        <Callout tone="info" title="Tại sao 1 engine + 3 SKU thắng">
          <Stack gap={6}>
            <Text>
              1. Chi phí biên của SKU thứ 2 và thứ 3 chủ yếu là <Text weight="semibold">vỏ
              client + ASO</Text>; lõi nội dung, mastery, API là một (§5.B.13 cross-mode mastery
              đã sẵn).
            </Text>
            <Text>
              2. Mỗi SKU phục vụ <Text weight="semibold">một “job to be done”</Text> khác nhau —
              khó nhồi cả 3 vào một câu pitch mà phụ huynh, trẻ, giáo viên cùng hiểu.
            </Text>
            <Text>
              3. Chính sách Google Play / App Store cho trẻ &lt;13:{" "}
              <Text weight="semibold">ads + IAP + leaderboard public</Text> không thể đặt cùng 1
              app “Designed for Families”. Tách SKU = tách compliance.
            </Text>
            <Text>
              4. Tách kênh phân phối: Flappy đẩy TikTok / Facebook Reels (viral), Candy đẩy
              Zalo/Facebook Group phụ huynh + KOL Toán, Arcade đi B2B trực tiếp đến trường &
              trung tâm — 3 funnel khác nhau hoàn toàn.
            </Text>
          </Stack>
        </Callout>
      </Stack>

      {/* ---------- 3. 3 SKU ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>3. Định nghĩa 3 SKU & nhiệm vụ chiến lược</H2>

        <Grid columns={3} gap={16}>
          <Card>
            <CardHeader>SKU-A · Flappy Math Blast (free + ads)</CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Row gap={6} wrap>
                  <Pill tone="info" size="sm" active>
                    Acquisition hook
                  </Pill>
                  <Pill size="sm" tone="neutral">
                    Sprint 60s
                  </Pill>
                  <Pill size="sm" tone="neutral">
                    Lớp 1–5
                  </Pill>
                </Row>
                <Text size="small" tone="secondary">
                  Vai trò trong portfolio
                </Text>
                <Text>
                  Cửa ngõ tiếp cận trẻ + viral marketing. Free, có quảng cáo bound by parental
                  consent, không IAP. KPI chính: D1/D7 retention, viral coefficient, conversion
                  sang Candy.
                </Text>
                <Text size="small" tone="secondary">
                  Mô hình thu
                </Text>
                <Text>
                  Ads rewarded (xem 15s → +1 Magic Feather), CPM ước tính 0,3–0,8 USD ở VN, target
                  ARPDAU 0,01–0,03 USD. Năm 1: 50–80% là kênh dẫn user, không phải kênh lợi nhuận.
                </Text>
                <Text size="small" tone="secondary">
                  Khách hàng mục tiêu
                </Text>
                <Text>
                  Trẻ 6–11 tự chơi trên điện thoại bố mẹ; phụ huynh tò mò muốn “thử nhanh”; KOL
                  TikTok thử thách Sprint 60s.
                </Text>
              </Stack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>SKU-B · Math Adventure 300 — Candy (subscription)</CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Row gap={6} wrap>
                  <Pill tone="success" size="sm" active>
                    Lõi doanh thu
                  </Pill>
                  <Pill size="sm" tone="neutral">
                    300 màn CT GDPT
                  </Pill>
                  <Pill size="sm" tone="neutral">
                    Parent dashboard
                  </Pill>
                </Row>
                <Text size="small" tone="secondary">
                  Vai trò trong portfolio
                </Text>
                <Text>
                  Cạnh tranh trực diện Monkey Math + OLM Toán. Là sản phẩm “học thay học thêm
                  online” cho phụ huynh. KPI chính: % trial → paid, MRR, churn 3-tháng,
                  parent-NPS.
                </Text>
                <Text size="small" tone="secondary">
                  Mô hình thu
                </Text>
                <Text>
                  3 tier: tháng 99K / năm 599K / family 3 con 999K VND. Free trial 7 ngày +
                  freemium 30 màn đầu (đến L030 hết World 1). Mục tiêu LTV / CAC ≥ 3.
                </Text>
                <Text size="small" tone="secondary">
                  Khách hàng mục tiêu
                </Text>
                <Text>
                  Phụ huynh đô thị 28–42 tuổi, con Lớp 1–3 là trọng tâm (anxiety cao nhất), Lớp 4–5
                  pre-cấp 2 + ViOlympic prep.
                </Text>
              </Stack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>SKU-C · Math Arcade Class (B2B/B2T)</CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Row gap={6} wrap>
                  <Pill tone="warning" size="sm" active>
                    B2B / B2T
                  </Pill>
                  <Pill size="sm" tone="neutral">
                    Giáo viên & trung tâm
                  </Pill>
                  <Pill size="sm" tone="neutral">
                    Bài tập tùy chỉnh
                  </Pill>
                </Row>
                <Text size="small" tone="secondary">
                  Vai trò trong portfolio
                </Text>
                <Text>
                  Mở mặt trận B2B doanh thu cao và phòng thủ trước đối thủ chỉ làm B2C. KPI chính:
                  số lớp/tháng, số bài giao, license renewal.
                </Text>
                <Text size="small" tone="secondary">
                  Mô hình thu
                </Text>
                <Text>
                  Free cho giáo viên 1 lớp ≤30 HS (acquisition). Pro 199K/tháng cho 5 lớp; bản
                  Trường 5–15tr/năm theo headcount; bản Trung tâm 3tr+ theo chi nhánh. Add-on báo
                  cáo PDF cho phụ huynh.
                </Text>
                <Text size="small" tone="secondary">
                  Khách hàng mục tiêu
                </Text>
                <Text>
                  ~360.000 giáo viên Tiểu học VN, ~14.500 trường Tiểu học, hàng nghìn trung tâm dạy
                  thêm Toán & gia sư 1-1.
                </Text>
              </Stack>
            </CardBody>
          </Card>
        </Grid>

        <Table
          headers={[
            "Khía cạnh",
            "SKU-A · Flappy",
            "SKU-B · Candy 300",
            "SKU-C · Arcade Class",
          ]}
          rows={[
            ["Job to be done", "Giải trí + luyện phản xạ", "Học bài bản theo chương trình", "Giao bài & đánh giá"],
            ["Người ra quyết định cài đặt", "Trẻ + phụ huynh thoáng", "Phụ huynh", "Giáo viên / quản lý trung tâm"],
            ["Độ dài phiên trung bình", "60 giây", "5–10 phút", "10–20 phút"],
            ["Mức cảm xúc cần dopamine", "Cao (vui)", "Vừa (tiến bộ)", "Thấp (chính xác)"],
            ["Yêu cầu compliance", "Ads cho trẻ <13, GDPR/COPPA-K", "Subscription quản lý, thông tin trẻ", "B2B contract, dữ liệu lớp"],
            ["Kênh phân phối chính", "App store, TikTok, Reels, YouTube Shorts", "Zalo, Facebook nhóm phụ huynh, KOL Toán", "Trực tiếp gặp BGH trường, hội thảo, đại lý vùng"],
            ["Đối thủ trực tiếp", "Prodigy, Khan Kids, hyper-casual maths", "Monkey Math, OLM Toán, Edupia Toán", "ClassPoint, Quizizz, Azota, Vio.edu.vn"],
            ["KPI ưu tiên", "DAU, viral, CAC ≈ 0", "MRR, paid conversion, churn", "Số trường ký, MAU giáo viên, NRR"],
            ["Năm 1 % doanh thu kỳ vọng", "5–10%", "55–65%", "25–35%"],
          ]}
          columnAlign={["left", "left", "left", "left"]}
          striped
        />
      </Stack>

      {/* ---------- 4. PHÂN KHÚC KHÁCH HÀNG ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>4. Phân khúc khách hàng mục tiêu (persona + sizing)</H2>
        <Text tone="secondary">
          Mỗi persona kèm dung lượng thị trường lý thuyết (TAM), nhu cầu cốt lõi, mode phù hợp và
          mức sẵn lòng chi trả tại thị trường VN 2026.
        </Text>

        <Table
          headers={[
            "Persona",
            "Quy mô VN",
            "Nhu cầu cốt lõi",
            "Mode phù hợp",
            "Willingness to pay",
            "Mức ưu tiên",
          ]}
          rows={[
            [
              "P1 · Phụ huynh đô thị có con Lớp 1–3",
              "~2,5 triệu hộ",
              "Lo CT GDPT 2018 mới, cần tool luyện hàng ngày, có báo cáo tiến bộ",
              "Candy (chính) + Flappy (mồi)",
              "300K–1tr / năm / con",
              "★★★★★",
            ],
            [
              "P2 · Phụ huynh con Lớp 4–5 luyện ViOlympic / lên cấp 2",
              "~1,2 triệu hộ",
              "Luyện tốc độ & câu khó, prep thi, ôn cửu chương + PS/TP",
              "Candy challenge L271–L300 + Flappy T4–T5",
              "500K–2tr / năm / con",
              "★★★★",
            ],
            [
              "P3 · Trẻ 6–11 tự chơi (intrinsic motivation)",
              "~9 triệu trẻ",
              "Vui, leaderboard, skin chim, sprint ngắn",
              "Flappy 60s (chính)",
              "Free; ads dung sai cao",
              "★★★★★ (kênh viral)",
            ],
            [
              "P4 · Giáo viên Tiểu học công lập",
              "~360.000 GV",
              "Bài tập 5–10 phút mở đầu/kết thúc tiết, dữ liệu lớp, không tốn chuẩn bị",
              "Arcade Class + Candy single-skill mode",
              "Cá nhân 0–200K/tháng",
              "★★★★",
            ],
            [
              "P5 · Trung tâm dạy thêm & gia sư 1-1",
              "Hàng chục nghìn TT + ~hàng trăm nghìn gia sư",
              "Bài luyện theo cấp HS, đo tiến bộ, in báo cáo gửi phụ huynh",
              "Arcade Class Pro + Candy report",
              "200K–500K/tháng/cơ sở",
              "★★★★",
            ],
            [
              "P6 · Trường Tiểu học (B2B school license)",
              "~14.500 trường",
              "Chuyển đổi số môn Toán, app dùng chung toàn trường, đáp ứng chỉ tiêu Sở GD",
              "Arcade Class School + Candy school edition",
              "5–30tr / năm / trường",
              "★★★ (sales-cycle dài)",
            ],
            [
              "P7 · Người Việt ở nước ngoài (Việt kiều)",
              "~5 triệu người, ~500K trẻ Lớp 1–5",
              "Giữ tiếng Việt + theo CT GDPT để con nắm Toán khi về thăm nhà",
              "Candy bản tiếng Việt + TTS rõ ràng",
              "USD pricing, sẵn lòng chi 30–80 USD/năm",
              "★★ (niche, biên lợi nhuận cao)",
            ],
            [
              "P8 · Phụ huynh nông thôn / tỉnh lẻ",
              "~3 triệu hộ có smartphone",
              "Toán bám SGK, ít data, offline khi cần, giá rẻ",
              "Flappy free + Candy gói nhỏ 30K/tháng",
              "30K–150K / năm / con",
              "★★★ (volume play)",
            ],
            [
              "P9 · Trẻ học chuyên biệt / SEN (chậm phát triển, tự kỷ nhẹ)",
              "~3–5% học sinh tiểu học",
              "Phiên cực ngắn, dopamine an toàn, không shame, TTS, accessibility",
              "Candy đầu World 1 + Flappy T1 (nhịp chậm)",
              "Phụ huynh chi cao 1–3tr/năm",
              "★★ (chứng chỉ đạo đức brand)",
            ],
          ]}
          columnAlign={["left", "left", "left", "left", "left", "left"]}
          striped
        />

        <Grid columns={2} gap={16}>
          <Card>
            <CardHeader>Ước lượng TAM / SAM / SOM năm 3</CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Text>
                  <Text weight="semibold">TAM</Text> — Toàn bộ chi tiêu của 9 triệu HS tiểu học VN
                  cho học Toán bổ trợ (offline + online): ước ~30.000 tỷ VND/năm.
                </Text>
                <Text>
                  <Text weight="semibold">SAM</Text> — Phần có thể đi đường digital app (đô thị +
                  có smartphone, chấp nhận thanh toán online): ~3 triệu hộ × 400K trung bình ≈
                  1.200 tỷ VND/năm (~$50M).
                </Text>
                <Text>
                  <Text weight="semibold">SOM năm 3</Text> — Mục tiêu chiếm 2–4% SAM = 24–48 tỷ VND
                  doanh thu/năm (~$1–2M ARR). Khả thi nếu đạt 80–150K paid family + 1.500 trường &
                  trung tâm.
                </Text>
              </Stack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>Vùng địa lý ưu tiên (năm 1–2)</CardHeader>
            <CardBody>
              <BarChart
                categories={["Hà Nội", "TP.HCM", "Đà Nẵng", "Hải Phòng", "Cần Thơ", "Tỉnh khác"]}
                series={[
                  {
                    name: "Mức ưu tiên (1–10)",
                    data: [10, 10, 7, 6, 5, 4],
                  },
                ]}
              />
              <Text tone="tertiary" size="small">
                Ưu tiên theo: GDP per capita, tỉ lệ smartphone, dung lượng KOL phụ huynh, kết quả
                ViOlympic (Hà Nội 7.733 / HP 4.396 thí sinh đoạt giải 2025–26).
              </Text>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      {/* ---------- 5. CẠNH TRANH ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>5. Định vị cạnh tranh</H2>
        <Table
          headers={[
            "Đối thủ",
            "Tập trung",
            "Điểm mạnh",
            "Điểm yếu (cơ hội cho Math Blast)",
            "Mode Math Blast đối đầu",
          ]}
          rows={[
            [
              "Monkey Math (VN)",
              "Mầm non + Lớp 1–2, song ngữ Anh",
              "Brand top, marketing mạnh, ARPU cao",
              "Lệch CT GDPT 2018 VN, nội dung Lớp 3–5 mỏng, chủ yếu tiếng Anh, giá cao",
              "Candy 300 (Lớp 1–5 thuần VN, bám SGK)",
            ],
            [
              "OLM.vn",
              "K-12, môn rộng, miễn phí + Pro",
              "Có sẵn cộng đồng giáo viên, content rộng",
              "UI cũ, không gamification kid-friendly, web-first",
              "Candy 300 + Arcade Class",
            ],
            [
              "ViOlympic / Vio.edu.vn",
              "Thi đấu Toán + tiếng Anh trực tuyến",
              "1 triệu thí sinh/năm, brand quốc dân",
              "Là arena thi, không phải tool luyện hàng ngày",
              "Tích hợp (làm “luyện thi ViOlympic”) thay vì cạnh tranh",
            ],
            [
              "Edupia Toán / Math",
              "Lớp 1–5, video bài giảng",
              "Video, phụ huynh dễ hiểu “con đang học gì”",
              "Tương tác thấp, không có loop chơi ngắn",
              "Candy + Flappy (game-first)",
            ],
            [
              "Khan Academy Kids (free)",
              "Free, đa môn, đa ngôn ngữ",
              "Miễn phí, chất lượng cao",
              "Không bám CT GDPT 2018, giọng/ngôn ngữ Tây",
              "Candy 300 (bám SGK & TTS giọng VN)",
            ],
            [
              "Prodigy Math",
              "RPG toán Bắc Mỹ",
              "Gameplay sâu, mạnh viral",
              "Không có ở VN, không bám SGK VN",
              "Flappy + Candy (game-first thuần VN)",
            ],
            [
              "Quizizz / Azota",
              "Tool giáo viên giao bài",
              "Hệ sinh thái giáo viên có sẵn",
              "Không Toán-first, không kid game",
              "Arcade Class (Toán + game-feel)",
            ],
            [
              "Hyper-casual maths trên CH Play",
              "Free + ads, không bám SGK",
              "Viral mạnh, CAC thấp",
              "Không tin cậy, nhanh chán, không có lộ trình",
              "Flappy (lấy độ vui + thêm chuẩn CT GDPT)",
            ],
          ]}
          rowTone={[
            "warning",
            undefined,
            "info",
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
          ]}
          striped
          columnAlign={["left", "left", "left", "left", "left"]}
        />

        <Callout tone="neutral" title="Định vị chốt — một câu cho mỗi đối tượng">
          <Stack gap={6}>
            <Text>
              <Text weight="semibold">Cho phụ huynh:</Text> “300 màn Toán bám SGK Lớp 1–5, có lộ
              trình & báo cáo tiến bộ — như học thêm Toán nhưng 25K/ngày, con tự ngồi 10 phút.”
            </Text>
            <Text>
              <Text weight="semibold">Cho trẻ:</Text> “Bay 3 nấc mỗi câu đúng — sprint 60 giây,
              chơi 1 phút giải lao, đứng top bảng gia đình.”
            </Text>
            <Text>
              <Text weight="semibold">Cho giáo viên:</Text> “Soạn bài luyện 60 giây trong 30 giây —
              giao cho cả lớp, có báo cáo tự động, dùng làm mở đầu/kết thúc tiết.”
            </Text>
          </Stack>
        </Callout>
      </Stack>

      {/* ---------- 6. SỨ MỆNH ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>6. Sứ mệnh & nguyên tắc bất biến</H2>

        <Card>
          <CardHeader>Tuyên ngôn sứ mệnh</CardHeader>
          <CardBody>
            <Stack gap={10}>
              <Text size="body" weight="semibold">
                “Giúp mỗi học sinh tiểu học Việt Nam yêu Toán — bằng những phiên chơi ngắn, an toàn
                tâm lý, bám sát Chương trình GDPT 2018, đồng hành cùng cha mẹ và thầy cô.”
              </Text>
              <Divider />
              <Text>
                Sứ mệnh cụ thể hoá thành 4 cam kết bất biến không đổi qua mọi thế hệ tính năng:
              </Text>
              <Stack gap={4}>
                <Text>
                  1. <Text weight="semibold">Bám chuẩn:</Text> Mọi content phải truy được về chuẩn
                  năng lực CT GDPT 2018 (Thông tư 32/2018) và có thể fork pack cho từng bộ SGK.
                </Text>
                <Text>
                  2. <Text weight="semibold">Tôn trọng trẻ em:</Text> Không loot box, không
                  variable-ratio reward, không leaderboard public ở MVP, không “lose streak”
                  cross-session ép trẻ quay lại (§5.B.12).
                </Text>
                <Text>
                  3. <Text weight="semibold">Minh bạch tiến bộ:</Text> Phụ huynh & giáo viên luôn
                  có dashboard số liệu — mastery, decay, đề xuất ôn — không chỉ điểm số mơ hồ.
                </Text>
                <Text>
                  4. <Text weight="semibold">Tiết kiệm & bền vững:</Text> Hạ tầng nhẹ (§9), 1
                  engine cho 3 SKU, content pack tái sử dụng — giảm chi phí biên để phục vụ cả phụ
                  huynh nông thôn 30K/tháng.
                </Text>
              </Stack>
            </Stack>
          </CardBody>
        </Card>

        <Grid columns={3} gap={12}>
          <Card>
            <CardHeader>Hứa hẹn với trẻ em</CardHeader>
            <CardBody>
              <Text>
                “Mỗi phiên 60 giây hoặc một màn vài phút, con luôn được khen. Sai cũng không bị
                trừng phạt — chỉ tụt nhẹ, được Lông Vũ Phép cứu. Mỗi tuần con khoá thêm một skin
                chim, leo thêm một nấc tri thức.”
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader>Hứa hẹn với phụ huynh</CardHeader>
            <CardBody>
              <Text>
                “Ba báo cáo / tuần qua Zalo: con đã master kỹ năng nào, đang kẹt ở đâu, gợi ý 10
                phút hôm nay. Không cần tự kiểm tra bài — Math Blast làm thay.”
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader>Hứa hẹn với giáo viên</CardHeader>
            <CardBody>
              <Text>
                “Giao bài luyện 1 phút trong 30 giây. Biết ngay học sinh nào yếu phép cộng, ai cần
                ôn nhân chia. Dạy chậm — Math Blast luyện nhanh.”
              </Text>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      {/* ---------- 7. MÔ HÌNH KINH DOANH ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>7. Mô hình kinh doanh tổng hợp</H2>
        <Grid columns={2} gap={16}>
          <Card>
            <CardHeader>Cơ cấu doanh thu kỳ vọng năm 3</CardHeader>
            <CardBody>
              <PieChart
                data={[
                  { label: "Subscription B2C (Candy 300)", value: 60, tone: "success" },
                  { label: "B2B trường + trung tâm (Arcade Class)", value: 25, tone: "warning" },
                  { label: "Ads & rewarded (Flappy)", value: 8, tone: "info" },
                  { label: "Việt kiều & xuất khẩu pack", value: 5, tone: "neutral" },
                  { label: "Phần thưởng & merchandise nhỏ", value: 2, tone: "neutral" },
                ]}
                donut
              />
              <Text tone="tertiary" size="small">
                Cơ cấu lành mạnh: 1 nguồn lõi (subscription) + 2 nguồn cân bằng + 2 niche.
              </Text>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>Giá kế hoạch (VND)</CardHeader>
            <CardBody>
              <Table
                headers={["Gói", "Giá", "Bao gồm"]}
                rows={[
                  ["Flappy free", "0", "Tất cả Tier, ads rewarded, không leaderboard public"],
                  ["Candy trial", "0 · 7 ngày", "Toàn bộ World 1 (L001–L054)"],
                  ["Candy Monthly", "99K / tháng", "1 con, mọi mode, parent dashboard"],
                  ["Candy Yearly", "599K / năm", "1 con, tiết kiệm 50%"],
                  ["Candy Family", "999K / năm", "Tối đa 3 con, share progress"],
                  ["Arcade Teacher Free", "0", "1 lớp ≤30 HS, báo cáo cơ bản"],
                  ["Arcade Teacher Pro", "199K / tháng", "5 lớp, báo cáo PDF, custom set"],
                  ["Arcade School", "5–30tr / năm", "License toàn trường, BI dashboard"],
                  ["Arcade Tutoring Center", "3tr+ / chi nhánh / năm", "Multi-class, phụ huynh login riêng"],
                ]}
                striped
                columnAlign={["left", "right", "left"]}
              />
            </CardBody>
          </Card>
        </Grid>

        <Grid columns={4} gap={12}>
          <Stat value="600K" label="Giá năm 1 con · Candy yearly (VND)" tone="success" />
          <Stat value="~$5" label="ARPU/tháng Candy quy đổi" />
          <Stat value="3–5×" label="Mục tiêu LTV / CAC" tone="info" />
          <Stat value="35–45%" label="Gross margin năm 2 kỳ vọng" tone="warning" />
        </Grid>
      </Stack>

      {/* ---------- 8. ROADMAP ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>8. Lộ trình go-to-market theo giai đoạn</H2>

        <Table
          headers={["Giai đoạn", "Tháng", "Hành động chính", "SKU chủ lực", "KPI gate"]}
          rows={[
            [
              "P0 · Validate",
              "0–2",
              "Pilot 100 phụ huynh Hà Nội + TP.HCM với MVP Candy World 1 + Flappy T1–T2",
              "Candy MVP",
              "≥40% phụ huynh sẵn sàng trả 99K/tháng",
            ],
            [
              "P1 · Acquisition",
              "2–5",
              "Mở Flappy public, đẩy TikTok/Reels, KOL Toán; thu user free; chuẩn bị paywall Candy",
              "Flappy",
              "10K DAU, viral coeff ≥0,3, CAC < 30K/install",
            ],
            [
              "P2 · Monetize B2C",
              "5–9",
              "Tung Candy Yearly + Family, parent dashboard, báo cáo Zalo, tích hợp ViOlympic prep",
              "Candy 300",
              "5.000 paid family, MRR ≥ 500tr VND",
            ],
            [
              "P3 · Mở B2B",
              "9–14",
              "Arcade Class Teacher Free; landed-and-expand 50 trường + 200 trung tâm",
              "Arcade Class",
              "200 lớp Pro + 20 trường ký năm",
            ],
            [
              "P4 · Scale",
              "14–24",
              "Mở pack SGK Cánh Diều / Chân Trời, mở leaderboard public anonymized, mở bản Việt kiều USD",
              "Cả 3 SKU",
              "ARR ≥ $1M, churn < 6%/tháng",
            ],
            [
              "P5 · Expand",
              "24–36",
              "Mở pack môn 2 (Tiếng Việt hoặc Khoa học); thử thị trường Indonesia/Philippines bản hoá",
              "Math Blast platform",
              "Pilot pack môn 2 đạt 1.000 paid",
            ],
          ]}
          rowTone={["info", undefined, "success", undefined, undefined, "warning"]}
          striped
        />

        <Callout
          tone="warning"
          title="Quyết định lùi thứ tự: vì sao Flappy ra trước Candy bản đầy đủ"
        >
          <Text>
            Mặc dù Candy là sản phẩm tạo doanh thu chính, Flappy nên ra mắt trước 1 nhịp vì: (i)
            chi phí mua user của một game free + viral &lt; 1/10 của một app subscription; (ii)
            Flappy reuse §5.B.15 manifest gọn — 4–6 tuần dev là đủ; (iii) data Flappy giúp pre-fill
            mastery cho user khi convert sang Candy → cảm giác “app hiểu con tôi từ đầu” — yếu tố
            quan trọng để phụ huynh trả tiền.
          </Text>
        </Callout>
      </Stack>

      {/* ---------- 9. RỦI RO ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>9. Rủi ro chính & cách giảm thiểu</H2>
        <Table
          headers={["Rủi ro", "Mức độ", "Giảm thiểu"]}
          rows={[
            [
              "CT GDPT 2018 thay đổi / có bản cập nhật giữa lộ trình",
              "Trung bình",
              "Manifest content pack tách rời engine (§5.A.7), cho phép fork không đụng code.",
            ],
            [
              "Phụ huynh không tin “game = học Toán nghiêm túc”",
              "Cao",
              "Báo cáo Zalo định kỳ + chứng nhận ViOlympic prep + endorsement giáo viên tiểu học có tiếng.",
            ],
            [
              "Lệ thuộc App Store / Google Play (chính sách trẻ <13 siết)",
              "Cao",
              "Có bản PWA độc lập + landing zalo mini-app, không phụ thuộc 100% store.",
            ],
            [
              "Cạnh tranh Monkey hạ giá / tung Monkey Math VN sâu hơn",
              "Cao",
              "Tận dụng 3 ngách Monkey yếu: Lớp 3–5, B2B trường, bám SGK thuần VN; ký hợp đồng độc quyền với KOL phụ huynh sớm.",
            ],
            [
              "Trung tâm dạy thêm bị siết quy định",
              "Trung bình",
              "Pivot B2B sang trường công + bản gia đình tự học (P1, P2) — sẵn lộ trình thay thế.",
            ],
            [
              "Trẻ chán nhanh / churn trong 14 ngày đầu",
              "Cao",
              "Bám pedagogy ngắn (60s + màn ngắn), Magic Feather + Soaring, time-cap soft 6 phiên/ngày — đầu tư mạnh §5.B.12.",
            ],
            [
              "Doanh thu ads thấp ở VN cho audience <13",
              "Trung bình",
              "Coi Flappy là kênh acquisition (cost center), không phải profit center; ngân sách Flappy nằm trong CAC của Candy.",
            ],
            [
              "Bảo mật & dữ liệu trẻ em",
              "Cao",
              "HMAC + idempotency (§9 doc), không lưu PII trẻ, parent là chủ tài khoản; sẵn nội dung cho audit pháp lý.",
            ],
          ]}
          rowTone={["info", "warning", "danger", "danger", undefined, "warning", undefined, "danger"]}
          striped
        />
      </Stack>

      {/* ---------- 10. KHUYẾN NGHỊ CHỐT ---------- */}
      <Divider />
      <Stack gap={12}>
        <H2>10. Khuyến nghị chiến lược cuối</H2>

        <Grid columns={2} gap={16}>
          <Card>
            <CardHeader>Việc nên làm ngay (next 30 ngày)</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text>
                  1. Chốt định vị 3 SKU dưới một thương hiệu “Math Blast” — đăng ký trademark, mua
                  tên miền cho từng SKU.
                </Text>
                <Text>
                  2. Phỏng vấn sâu 20 phụ huynh + 10 giáo viên + 10 trung tâm — verify
                  willingness-to-pay và 3 lý do từ chối hàng đầu.
                </Text>
                <Text>
                  3. Quyết định content pack đầu là <Text weight="semibold">“Kết nối tri thức với
                  cuộc sống”</Text> (đã ghi trong §3.2) và lập manifest L001–L054 hoàn chỉnh để
                  pilot.
                </Text>
                <Text>
                  4. Build Flappy T1–T2 vertical slice (4 tuần) để có công cụ đo virality trước
                  khi đốt ngân sách Candy.
                </Text>
                <Text>
                  5. Lên kế hoạch hợp tác 2–3 KOL phụ huynh Toán + 1 hiệu trưởng tiểu học cho
                  endorsement sớm.
                </Text>
              </Stack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>Việc không nên làm</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text>
                  • Không tung 3 app ngay từ đầu — vượt năng lực vận hành, loãng marketing
                  budget.
                </Text>
                <Text>
                  • Không cạnh tranh trực diện Monkey ở mầm non — họ quá mạnh ở đó, lợi thế Math
                  Blast là Lớp 3–5 và B2B.
                </Text>
                <Text>
                  • Không mở leaderboard public hay loot box trong 12 tháng đầu — rủi ro brand
                  &amp; pháp lý cao.
                </Text>
                <Text>
                  • Không kéo dài tính năng vô tận trong MVP Candy — phải dừng ở World 1 + Flappy
                  T1–T2 để pilot, không build 300 màn rồi mới ra mắt.
                </Text>
                <Text>
                  • Không hứa “tăng điểm thi cụ thể” — vi phạm quảng cáo giáo dục VN; chỉ hứa
                  mastery rõ ràng theo skill_id.
                </Text>
              </Stack>
            </CardBody>
          </Card>
        </Grid>

        <Callout tone="success" title="Hướng đi chiến lược tổng quát">
          <Stack gap={6}>
            <Text>
              <Text weight="semibold">Định vị:</Text> Math Blast là <Text italic>nền tảng học và
              chơi Toán Tiểu học Việt Nam, bám chuẩn CT GDPT 2018</Text>, không phải “game maths
              quốc tế dịch sang tiếng Việt”.
            </Text>
            <Text>
              <Text weight="semibold">Sản phẩm:</Text> Một engine + ba SKU phân tuyến rõ — Flappy
              (viral hook), Candy 300 (lõi subscription), Arcade Class (B2B).
            </Text>
            <Text>
              <Text weight="semibold">Tài chính:</Text> Năm 1 hoà vốn vận hành, năm 2 dương biên,
              năm 3 đạt $1M ARR — đường lên dựa trên Candy + B2B chứ không phải ads.
            </Text>
            <Text>
              <Text weight="semibold">Sứ mệnh:</Text> Giúp trẻ em VN yêu Toán — bằng phiên ngắn, an
              toàn, minh bạch tiến bộ, đồng hành cha mẹ &amp; thầy cô. Mọi quyết định tính năng
              phải kiểm tra ngược lại 4 cam kết bất biến ở §6.
            </Text>
          </Stack>
        </Callout>

        <Text tone="tertiary" size="small">
          Tài liệu phân tích đính kèm tham chiếu math-blast-v2.md các mục §3, §5.A, §5.B, §6, §9. Số
          liệu thị trường: GlobalData VN EdTech 2024, IMARC 2025, Tuổi Trẻ / VietnamPlus
          ViOlympic 2025–26, Thanh Niên / VTC News chi phí học thêm 2025–26.
        </Text>
      </Stack>
    </Stack>
  );
}
