# 20251193
/*
 * stack_animation.cpp
 *
 * 스택 연산(push/pop/top) 애니메이션을 MP4로 출력하는 C++ 프로그램
 * 빌드: g++ stack_animation.cpp -o stack_animation \
 *         $(pkg-config --cflags --libs cairo freetype2) -std=c++17
 * 실행: ./stack_animation
 * 결과: stack_animation.mp4 (FFmpeg 필요)
 */
 
#include <cairo/cairo.h>
#include <cairo/cairo-ft.h>
#include <ft2build.h>
#include FT_FREETYPE_H
 
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <filesystem>
 
// ─── 캔버스 설정 ──────────────────────────────────────────────
static const int W         = 1560;   // 픽셀 너비
static const int H         = 900;    // 픽셀 높이
static const int FPS       = 30;
static const int FRAMES_PER_STEP = 28;
static const int HOLD_FRAMES     = 60;   // 마지막 단계 유지 프레임
 
// ─── 색상 헬퍼 ────────────────────────────────────────────────
struct Color { double r, g, b, a; };
 
static Color hex(const char* h, double alpha = 1.0) {
    unsigned int v;
    sscanf(h + (*h == '#'), "%06x", &v);
    return { ((v>>16)&0xFF)/255.0, ((v>>8)&0xFF)/255.0, (v&0xFF)/255.0, alpha };
}
 
static void setc(cairo_t* cr, Color c) {
    cairo_set_source_rgba(cr, c.r, c.g, c.b, c.a);
}
 
// ─── 둥근 사각형 ─────────────────────────────────────────────
static void roundRect(cairo_t* cr, double x, double y, double w, double h, double r) {
    cairo_new_sub_path(cr);
    cairo_arc(cr, x+w-r, y+r,   r, -M_PI/2,  0);
    cairo_arc(cr, x+w-r, y+h-r, r,  0,        M_PI/2);
    cairo_arc(cr, x+r,   y+h-r, r,  M_PI/2,   M_PI);
    cairo_arc(cr, x+r,   y+r,   r,  M_PI,     3*M_PI/2);
    cairo_close_path(cr);
}
 
// ─── 팔레트 ──────────────────────────────────────────────────
static const char* ITEM_BG[]  = {"#B5D4F4","#C0DD97","#F5C4B3","#CECBF6","#9FE1CB","#FAC775","#F4C0D1"};
static const char* ITEM_FG[]  = {"#0C447C","#27500A","#712B13","#3C3489","#085041","#633806","#72243E"};
static const int   PALETTE_N  = 7;
static const char* OP_BG[]    = {"#EAF3DE","#FCEBEB","#E6F1FB","#F1EFE8"};  // push pop top init
static const char* OP_FG[]    = {"#27500A","#791F1F","#0C447C","#5F5E5A"};
 
static int opIndex(const std::string& op) {
    if (op=="push") return 0;
    if (op=="pop")  return 1;
    if (op=="top")  return 2;
    return 3;
}
 
// ─── 스텝 정의 ───────────────────────────────────────────────
struct Step {
    std::string op;
    std::string code;
    std::vector<std::string> stack;
    std::string msg;
};
 
static std::vector<Step> STEPS = {
    {"init",  "stack = []",                    {},                                                         "stack 선언 완료"},
    {"push",  "stack.append('커피')",            {"커피"},                                                   "push('커피')"},
    {"top",   "top = stack[-1]  # '커피'",       {"커피"},                                                   "top() → '커피'"},
    {"push",  "stack.append('중간고사')",         {"커피","중간고사"},                                          "push('중간고사')"},
    {"push",  "stack.append('벚꽃')",             {"커피","중간고사","벚꽃"},                                   "push('벚꽃')"},
    {"top",   "top = stack[-1]  # '벚꽃'",       {"커피","중간고사","벚꽃"},                                   "top() → '벚꽃'"},
    {"push",  "stack.append('두쫀쿠')",           {"커피","중간고사","벚꽃","두쫀쿠"},                          "push('두쫀쿠')"},
    {"push",  "stack.append('버터떡')",           {"커피","중간고사","벚꽃","두쫀쿠","버터떡"},                 "push('버터떡')"},
    {"pop",   "val = stack.pop()  # '버터떡'",    {"커피","중간고사","벚꽃","두쫀쿠"},                          "pop() → '버터떡' 제거"},
    {"push",  "stack.append('케이크')",           {"커피","중간고사","벚꽃","두쫀쿠","케이크"},                 "push('케이크')"},
    {"push",  "stack.append('공부')",             {"커피","중간고사","벚꽃","두쫀쿠","케이크","공부"},           "push('공부')"},
    {"top",   "top = stack[-1]  # '공부'",       {"커피","중간고사","벚꽃","두쫀쿠","케이크","공부"},           "top() → '공부'"},
    {"pop",   "val = stack.pop()  # '공부'",     {"커피","중간고사","벚꽃","두쫀쿠","케이크"},                  "pop() → '공부' 제거"},
    {"pop",   "val = stack.pop()  # '케이크'",   {"커피","중간고사","벚꽃","두쫀쿠"},                           "pop() → '케이크' 제거"},
    {"top",   "top = stack[-1]  # '두쫀쿠'",     {"커피","중간고사","벚꽃","두쫀쿠"},                           "top() → '두쫀쿠'"},
};
 
// ─── FreeType / Cairo 폰트 ────────────────────────────────────
static FT_Library  ftLib;
static FT_Face     ftFace;
static cairo_font_face_t* cairoCJK = nullptr;
 
static void initFont(const char* path) {
    FT_Init_FreeType(&ftLib);
    FT_New_Face(ftLib, path, 0, &ftFace);
    cairoCJK = cairo_ft_font_face_create_for_ft_face(ftFace, 0);
}
 
static void setFont(cairo_t* cr, double size) {
    if (cairoCJK) cairo_set_font_face(cr, cairoCJK);
    cairo_set_font_size(cr, size);
}
 
// ─── 텍스트 유틸 ─────────────────────────────────────────────
static void drawText(cairo_t* cr, double x, double y, const std::string& txt,
                     double size, Color col, bool centerX = false, bool centerY = false) {
    setFont(cr, size);
    if (centerX || centerY) {
        cairo_text_extents_t ext;
        cairo_text_extents(cr, txt.c_str(), &ext);
        if (centerX) x -= ext.width/2 + ext.x_bearing;
        if (centerY) y -= ext.height/2 + ext.y_bearing;
    }
    setc(cr, col);
    cairo_move_to(cr, x, y);
    cairo_show_text(cr, txt.c_str());
}
 
// 텍스트 너비 측정
static double textWidth(cairo_t* cr, const std::string& txt, double size) {
    setFont(cr, size);
    cairo_text_extents_t ext;
    cairo_text_extents(cr, txt.c_str(), &ext);
    return ext.width;
}
 
// ─── easing ──────────────────────────────────────────────────
static double easeOut(double t) { return 1 - (1-t)*(1-t); }
static double easeIn (double t) { return t*t; }
 
// ─── 프레임 렌더링 ───────────────────────────────────────────
static void renderFrame(cairo_t* cr, int stepIdx, int frameInStep, int totalFrames) {
    double t = (totalFrames <= 1) ? 1.0 : (double)frameInStep / (totalFrames - 1);
    const Step& s    = STEPS[stepIdx];
    const std::vector<std::string>& curr = s.stack;
    const std::vector<std::string>& prev = (stepIdx > 0) ? STEPS[stepIdx-1].stack : std::vector<std::string>{};
 
    // 배경
    setc(cr, hex("#FAFAF8"));
    cairo_paint(cr);
 
    // ─── 제목 ───────────────────────────────────────────────
    drawText(cr, W/2.0, 58, "Python 스택(Stack) 연산 애니메이션",
             32, hex("#2C2C2A"), true, true);
 
    // ════════════════════════════════════════════════════════
    //  LEFT PANEL  (0 ~ W/2)
    // ════════════════════════════════════════════════════════
    double lx = 40, lw = W/2.0 - 60;
 
    // 패널 레이블
    drawText(cr, lx + lw/2, 100, "스택 시각화",
             22, hex("#888780"), true, true);
 
    // 스택 컨테이너
    const double ITEM_H    = 72.0;
    const double MAX_ITEMS = 10;
    const double CONT_PAD  = 16;
    const double CONT_X    = lx + 20;
    const double CONT_W    = lw - 40;
    const double CONT_H    = MAX_ITEMS * ITEM_H + CONT_PAD * 2;
    const double CONT_Y    = H - 100 - CONT_H;
 
    roundRect(cr, CONT_X, CONT_Y, CONT_W, CONT_H, 12);
    setc(cr, hex("#F0EEE8")); cairo_fill_preserve(cr);
    setc(cr, hex("#CCCAC0")); cairo_set_line_width(cr, 2); cairo_stroke(cr);
 
    // "bottom" 레이블
    drawText(cr, CONT_X + CONT_W/2, CONT_Y + CONT_H + 30,
             "bottom", 18, hex("#CCCCCC"), true, true);
 
    // 아이템 그리기
    auto itemY = [&](int i) -> double {
        return CONT_Y + CONT_H - CONT_PAD - (i+1)*ITEM_H + 4;
    };
 
    for (int i = 0; i < (int)curr.size(); i++) {
        const std::string& item = curr[i];
        int ci = i % PALETTE_N;
        Color fc = hex(ITEM_BG[ci]);
        Color tc = hex(ITEM_FG[ci]);
 
        bool isNew = (std::find(prev.begin(), prev.end(), item) == prev.end())
                     && (s.op == "push");
        double oy = itemY(i);
        double alpha = 1.0;
        if (isNew) {
            double et = easeOut(t);
            oy += (1.0 - et) * (-ITEM_H * 2.0);
            alpha = t;
        }
 
        // 배경 박스
        fc.a = alpha;
        roundRect(cr, CONT_X + 10, oy, CONT_W - 20, ITEM_H - 8, 10);
        setc(cr, fc); cairo_fill(cr);
 
        // top 강조 테두리
        bool isTop = (i == (int)curr.size()-1);
        if (isTop) {
            roundRect(cr, CONT_X + 6, oy - 4, CONT_W - 12, ITEM_H, 12);
            setc(cr, hex("#378ADD", alpha)); cairo_set_line_width(cr, 3);
            cairo_stroke(cr);
        }
 
        // 아이템 이름
        tc.a = alpha;
        drawText(cr, CONT_X + CONT_W*0.38, oy + ITEM_H/2 - 4,
                 item, 22, tc, true, true);
        // 인덱스
        Color ic = tc; ic.a *= 0.6;
        drawText(cr, CONT_X + CONT_W*0.78, oy + ITEM_H/2 - 4,
                 "[" + std::to_string(i) + "]", 17, ic, true, true);
    }
 
    // pop 아이템 날아가는 애니메이션
    if (s.op == "pop" && prev.size() > curr.size()) {
        const std::string& popped = prev.back();
        int ci = ((int)prev.size()-1) % PALETTE_N;
        double base_y = itemY((int)prev.size()-1);
        double fly_y  = base_y - easeIn(t) * ITEM_H * 1.8;
        double fly_x  = easeIn(t) * CONT_W * 0.35;
        double alpha  = std::max(0.0, 1.0 - t * 1.5);
 
        Color fc2 = hex(ITEM_BG[ci], alpha);
        roundRect(cr, CONT_X + 10 + fly_x, fly_y, CONT_W - 20, ITEM_H - 8, 10);
        setc(cr, fc2); cairo_fill(cr);
 
        Color tc2 = hex(ITEM_FG[ci], alpha);
        drawText(cr, CONT_X + CONT_W*0.38 + fly_x, fly_y + ITEM_H/2 - 4,
                 popped, 22, tc2, true, true);
    }
 
    // top 화살표
    if (!curr.empty()) {
        double top_y = itemY((int)curr.size()-1) + ITEM_H/2 - 4;
        drawText(cr, CONT_X + CONT_W + 18, top_y,
                 "← top", 20, hex("#378ADD"), false, true);
    }
 
    // 크기 표시
    drawText(cr, CONT_X + CONT_W/2, CONT_Y - 18,
             "크기: " + std::to_string(curr.size()) + " / 10",
             20, hex("#5F5E5A"), true, true);
 
    // ════════════════════════════════════════════════════════
    //  RIGHT PANEL  (W/2 ~ W)
    // ════════════════════════════════════════════════════════
    double rx = W/2.0 + 20, rw = W/2.0 - 60;
    double ry0 = 88;
 
    // 단계 표시
    drawText(cr, rx + rw/2, ry0 + 18,
             "단계  " + std::to_string(stepIdx+1) + " / " + std::to_string((int)STEPS.size()),
             20, hex("#888780"), true, true);
 
    // op 배지
    int oi = opIndex(s.op);
    double badge_y = ry0 + 40;
    roundRect(cr, rx, badge_y, rw, 70, 12);
    setc(cr, hex(OP_BG[oi])); cairo_fill(cr);
    drawText(cr, rx + rw/2, badge_y + 35 + 10,
             "연산: " + s.op + "()", 26, hex(OP_FG[oi]), true, true);
 
    // 메시지 박스
    double msg_y = badge_y + 82;
    roundRect(cr, rx, msg_y, rw, 64, 10);
    setc(cr, hex("#FFFFFF")); cairo_fill_preserve(cr);
    setc(cr, hex("#D3D1C7")); cairo_set_line_width(cr, 1); cairo_stroke(cr);
    drawText(cr, rx + rw/2, msg_y + 32 + 10,
             s.msg, 22, hex("#2C2C2A"), true, true);
 
    // 코드 박스
    double code_y = msg_y + 76;
    roundRect(cr, rx, code_y, rw, 80, 10);
    setc(cr, hex("#F1EFE8")); cairo_fill_preserve(cr);
    setc(cr, hex("#D3D1C7")); cairo_set_line_width(cr, 1); cairo_stroke(cr);
    // 코드는 모노 폰트
    cairo_select_font_face(cr, "monospace", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL);
    cairo_set_font_size(cr, 19);
    setc(cr, hex("#2C2C2A"));
    cairo_move_to(cr, rx + 18, code_y + 46);
    cairo_show_text(cr, s.code.c_str());
    // 다시 CJK 폰트 복원
    if (cairoCJK) cairo_set_font_face(cr, cairoCJK);
 
    // top 값
    double tv_y = code_y + 96;
    drawText(cr, rx + 18,  tv_y, "top 값:", 21, hex("#5F5E5A"));
    std::string topVal = curr.empty() ? "-" : curr.back();
    drawText(cr, rx + rw - 18, tv_y, topVal, 22, hex("#185FA5"),
             false, false);
    // right-align top value
    {
        double tw = textWidth(cr, topVal, 22);
        cairo_move_to(cr, rx + rw - 18 - tw, tv_y);
        setc(cr, hex("#185FA5"));
        cairo_show_text(cr, topVal.c_str());
    }
 
    // 연산 기록
    double log_y = tv_y + 38;
    drawText(cr, rx + 18, log_y, "연산 기록:", 20, hex("#5F5E5A"));
 
    int logStart = std::max(0, stepIdx - 5);
    int logCount = stepIdx + 1 - logStart;
    for (int li = 0; li < logCount; li++) {
        int si = stepIdx - li;
        if (si < 0) break;
        double ly = log_y + 32 + li * 52.0;
        if (ly > H - 100) break;
        const Step& ls = STEPS[si];
        int loi = opIndex(ls.op);
 
        // 배지
        roundRect(cr, rx + 10, ly - 18, 90, 34, 8);
        setc(cr, hex(OP_BG[loi])); cairo_fill(cr);
        drawText(cr, rx + 55, ly, ls.op, 17, hex(OP_FG[loi]), true, true);
 
        // 메시지
        Color lc = (li == 0) ? hex("#2C2C2A") : hex("#888780");
        drawText(cr, rx + 115, ly, ls.msg, 18, lc, false, true);
    }
 
    // ─── 진행 바 ─────────────────────────────────────────
    double bar_x = 40, bar_y = H - 42, bar_w = W - 80.0, bar_h = 14;
    roundRect(cr, bar_x, bar_y, bar_w, bar_h, 7);
    setc(cr, hex("#E8E6E0")); cairo_fill(cr);
    double prog = (stepIdx + t) / ((int)STEPS.size() - 1);
    if (prog > 0.002) {
        roundRect(cr, bar_x, bar_y, bar_w * prog, bar_h, 7);
        setc(cr, hex("#378ADD")); cairo_fill(cr);
    }
    // 구분선
    setc(cr, hex("#D3D1C7")); cairo_set_line_width(cr, 1);
    cairo_move_to(cr, W/2.0 - 10, 80);
    cairo_line_to(cr, W/2.0 - 10, H - 55);
    cairo_stroke(cr);
}
 
// ─── PNG 저장 ────────────────────────────────────────────────
static void saveFrame(cairo_surface_t* surf, const char* path) {
    cairo_surface_write_to_png(surf, path);
}
 
// ─── main ────────────────────────────────────────────────────
int main() {
    const char* FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc";
    initFont(FONT_PATH);
 
    // 프레임 목록 구성
    struct FrameInfo { int step, frameIn, total; };
    std::vector<FrameInfo> frames;
    for (int i = 0; i < (int)STEPS.size(); i++) {
        int total = (i == (int)STEPS.size()-1) ? HOLD_FRAMES : FRAMES_PER_STEP;
        for (int f = 0; f < total; f++)
            frames.push_back({i, f, total});
    }
    printf("총 프레임: %d (%.1f초)\n", (int)frames.size(), frames.size()/(double)FPS);
 
    // 임시 프레임 디렉터리
    std::filesystem::create_directories("/tmp/stack_frames");
 
    cairo_surface_t* surf = cairo_image_surface_create(CAIRO_FORMAT_RGB24, W, H);
    cairo_t* cr = cairo_create(surf);
 
    printf("프레임 렌더링 중...\n");
    for (int fi = 0; fi < (int)frames.size(); fi++) {
        auto& f = frames[fi];
        renderFrame(cr, f.step, f.frameIn, f.total);
        char path[256];
        snprintf(path, sizeof(path), "/tmp/stack_frames/frame_%05d.png", fi);
        saveFrame(surf, path);
        if (fi % 30 == 0) printf("  %d / %d\n", fi, (int)frames.size());
    }
 
    cairo_destroy(cr);
    cairo_surface_destroy(surf);
    cairo_font_face_destroy(cairoCJK);
    FT_Done_Face(ftFace);
    FT_Done_FreeType(ftLib);
 
    printf("FFmpeg으로 MP4 인코딩 중...\n");
    char cmd[512];
    snprintf(cmd, sizeof(cmd),
        "ffmpeg -y -framerate %d -i /tmp/stack_frames/frame_%%05d.png "
        "-vcodec libx264 -pix_fmt yuv420p -crf 20 "
        "/mnt/user-data/outputs/stack_animation_cpp.mp4",
        FPS);
    int ret = system(cmd);
    if (ret == 0)
        printf("완료: stack_animation_cpp.mp4\n");
    else
        fprintf(stderr, "FFmpeg 오류 (code=%d)\n", ret);
 
    // 임시 파일 정리
    system("rm -rf /tmp/stack_frames");
    return ret;
}
