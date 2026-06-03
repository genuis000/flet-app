import flet as ft
import requests
import re

API_KEY = "ark-4c611126-b38d-4176-899d-8c01dcc99581-24332"
ENDPOINT_ID = "doubao-1-5-pro-32k-250115"
URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

def get_nutrition_report(info):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    system_prompt = (
        "你是专业青少年营养师，依据用户完整问卷信息，生成一份个性化营养健康报告。"
        "请严格按照以下格式输出，语言活泼亲切，多用表情符号，避免复杂表格：\n\n"
        "# 🍎 青少年专属营养健康报告\n\n"
        "## 📊 一、身体综合评估\n"
        "- 用简洁的语言描述整体健康状况\n"
        "- 需要生成BMI、提及生长发育趋势等\n\n"
        "## 🚨 二、现存饮食&健康隐患\n"
        "- 列出1-3个主要问题\n"
        "- 每个问题用'⚠️ '开头\n\n"
        "## 🥗 三、定制三餐食谱\n"
        "- **早餐**：具体食物搭配（含分量建议）\n"
        "- **午餐**：具体食物搭配（含分量建议）\n"
        "- **晚餐**：具体食物搭配（含分量建议）\n"
        "- **加餐（可选）**：健康小零食推荐\n\n"
        "## 🍬 四、零食与日常饮食调整方案\n"
        "- 用'✅ '开头列出2-3条具体可执行建议\n\n"
        "## 🏃 五、运动作息规划\n"
        "- **运动建议**：每周运动次数、每次时长、推荐运动类型\n"
        "- **作息建议**：早睡早起的具体时间点\n\n"
        "## 💡 六、针对性改善建议\n"
        "- 用'💡 '开头列出2-3条核心改善建议"
    )
    data = {
        "model": ENDPOINT_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户完整问卷数据：{info}"}
        ]
    }
    try:
        res = requests.post(URL, json=data, headers=headers, timeout=30)
        res.raise_for_status()
        res_json = res.json()
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return res_json["choices"][0]["message"]["content"]
        else:
            return f"接口返回异常：{res_json}"
    except requests.exceptions.RequestException as e:
        return f"API调用失败：{str(e)}"
    except ValueError:
        return f"JSON解析失败，响应内容：{res.text}"

def bind_single_checkbox(check_list):
    def on_ck_change(e):
        target = e.control
        if target.value:
            for ck in check_list:
                if ck != target:
                    ck.value = False
        target.page.update()
    for ck in check_list:
        ck.on_change = on_ck_change

def validate_inputs(age, height, weight, grade, sex_cks):
    errors = []
    sex_selected = any(ck.value for ck in sex_cks)
    if not sex_selected:
        errors.append("请选择性别")
    if not age.value:
        errors.append("请填写年龄")
    elif not age.value.isdigit() or not (6 <= int(age.value) <= 20):
        errors.append("年龄必须是6-20之间的数字")
    if not height.value:
        errors.append("请填写身高")
    elif not re.match(r'^\d{2,3}$', height.value) or not (100 <= int(height.value) <= 220):
        errors.append("身高必须是100-220之间的整数(cm)")
    if not weight.value:
        errors.append("请填写体重")
    elif not re.match(r'^\d{1,3}(\.\d{1,2})?$', weight.value) or not (20 <= float(weight.value) <= 150):
        errors.append("体重必须是20-150之间的数字(kg)")
    if not grade.value:
        errors.append("请填写年级")
    return errors

def main(page: ft.Page):
    # 手机核心适配配置
    page.title = "青少年营养健康测评"
    page.padding = 10
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ALWAYS
    page.window_min_width = 320

    # 性别（纯竖向）
    ck_male = ft.Checkbox("男", value=False)
    ck_female = ft.Checkbox("女", value=False)
    sex_cks = [ck_male, ck_female]
    bind_single_checkbox(sex_cks)

    # 所有输入框单独一行（纯竖向）
    age = ft.TextField(label="年龄(岁)", hint_text="6-20岁", keyboard_type=ft.KeyboardType.NUMBER)
    height = ft.TextField(label="身高(cm)", hint_text="100-220", keyboard_type=ft.KeyboardType.NUMBER)
    weight = ft.TextField(label="体重(kg)", hint_text="20-150", keyboard_type=ft.KeyboardType.NUMBER)
    grade = ft.TextField(label="就读年级", hint_text="如：初一、高一")

    # 家族病史
    ck_fam_none = ft.Checkbox(label="无")
    ck_fat = ft.Checkbox(label="肥胖")
    ck_hbp = ft.Checkbox(label="高血压")
    ck_dm = ft.Checkbox(label="糖尿病")
    ck_hlip = ft.Checkbox(label="高血脂")
    ck_gout = ft.Checkbox(label="痛风")
    fam_col = ft.Column([ck_fam_none, ck_fat, ck_hbp, ck_dm, ck_hlip, ck_gout], spacing=4)

    # 膳食习惯（全部竖向）
    ck_b1 = ft.Checkbox("每日")
    ck_b2 = ft.Checkbox("每周4–6天")
    ck_b3 = ft.Checkbox("每周1–3天")
    ck_b4 = ft.Checkbox("从不")
    breakfast_cks = [ck_b1,ck_b2,ck_b3,ck_b4]
    bind_single_checkbox(breakfast_cks)

    ck_l1 = ft.Checkbox("基本定时")
    ck_l2 = ft.Checkbox("经常不准时")
    ck_l3 = ft.Checkbox("饥一顿饱一顿")
    lunch_cks = [ck_l1,ck_l2,ck_l3]
    bind_single_checkbox(lunch_cks)

    ck_v1=ft.Checkbox("每天");ck_v2=ft.Checkbox("5–6天");ck_v3=ft.Checkbox("3–4天");ck_v4=ft.Checkbox("1–2天");ck_v5=ft.Checkbox("几乎不吃")
    veg_cks=[ck_v1,ck_v2,ck_v3,ck_v4,ck_v5];bind_single_checkbox(veg_cks)
    ck_fr1=ft.Checkbox("每天");ck_fr2=ft.Checkbox("5–6天");ck_fr3=ft.Checkbox("3–4天");ck_fr4=ft.Checkbox("1–2天");ck_fr5=ft.Checkbox("几乎不吃")
    fruit_cks=[ck_fr1,ck_fr2,ck_fr3,ck_fr4,ck_fr5];bind_single_checkbox(fruit_cks)
    ck_mi1=ft.Checkbox("每天");ck_mi2=ft.Checkbox("5–6天");ck_mi3=ft.Checkbox("3–4天");ck_mi4=ft.Checkbox("1–2天");ck_mi5=ft.Checkbox("几乎不吃")
    milk_cks=[ck_mi1,ck_mi2,ck_mi3,ck_mi4,ck_mi5];bind_single_checkbox(milk_cks)
    ck_me1=ft.Checkbox("每天");ck_me2=ft.Checkbox("5–6天");ck_me3=ft.Checkbox("3–4天");ck_me4=ft.Checkbox("1–2天");ck_me5=ft.Checkbox("几乎不吃")
    meat_cks=[ck_me1,ck_me2,ck_me3,ck_me4,ck_me5];bind_single_checkbox(meat_cks)
    ck_fi1=ft.Checkbox("每周3次以上");ck_fi2=ft.Checkbox("每周1–2次");ck_fi3=ft.Checkbox("每月1–2次");ck_fi4=ft.Checkbox("几乎不吃")
    fish_cks=[ck_fi1,ck_fi2,ck_fi3,ck_fi4];bind_single_checkbox(fish_cks)
    ck_e1=ft.Checkbox("每天1个及以上");ck_e2=ft.Checkbox("隔天1个");ck_e3=ft.Checkbox("每周2–3个");ck_e4=ft.Checkbox("很少吃")
    egg_cks=[ck_e1,ck_e2,ck_e3,ck_e4];bind_single_checkbox(egg_cks)
    ck_sn1=ft.Checkbox("从不吃");ck_sn2=ft.Checkbox("每周1–2次");ck_sn3=ft.Checkbox("每周3–5次");ck_sn4=ft.Checkbox("每天都吃")
    snack_cks=[ck_sn1,ck_sn2,ck_sn3,ck_sn4];bind_single_checkbox(snack_cks)
    ck_dr1=ft.Checkbox("从不喝");ck_dr2=ft.Checkbox("每周1–2次");ck_dr3=ft.Checkbox("每周3–5次");ck_dr4=ft.Checkbox("每天都喝")
    drink_cks=[ck_dr1,ck_dr2,ck_dr3,ck_dr4];bind_single_checkbox(drink_cks)
    ck_fry1=ft.Checkbox("从不吃");ck_fry2=ft.Checkbox("每周1–2次");ck_fry3=ft.Checkbox("每周3–5次");ck_fry4=ft.Checkbox("每天都吃")
    fry_cks=[ck_fry1,ck_fry2,ck_fry3,ck_fry4];bind_single_checkbox(fry_cks)
    ck_st1=ft.Checkbox("精米白面为主");ck_st2=ft.Checkbox("经常吃粗粮/杂粮");ck_st3=ft.Checkbox("基本不吃主食")
    staple_cks=[ck_st1,ck_st2,ck_st3];bind_single_checkbox(staple_cks)
    ck_ta1=ft.Checkbox("清淡");ck_ta2=ft.Checkbox("偏咸");ck_ta3=ft.Checkbox("偏甜");ck_ta4=ft.Checkbox("偏油腻、重辣")
    taste_cks=[ck_ta1,ck_ta2,ck_ta3,ck_ta4];bind_single_checkbox(taste_cks)
    ck_sp1=ft.Checkbox("细嚼慢咽");ck_sp2=ft.Checkbox("速度正常");ck_sp3=ft.Checkbox("吃饭很快")
    speed_cks=[ck_sp1,ck_sp2,ck_sp3];bind_single_checkbox(speed_cks)
    ck_ni1=ft.Checkbox("无");ck_ni2=ft.Checkbox("偶尔(≤2次/周)");ck_ni3=ft.Checkbox("经常(≥3次/周)")
    night_cks=[ck_ni1,ck_ni2,ck_ni3];bind_single_checkbox(night_cks)

    # 运动（竖向）
    ck_spw1=ft.Checkbox("0次");ck_spw2=ft.Checkbox("1–2次");ck_spw3=ft.Checkbox("3–4次");ck_spw4=ft.Checkbox("5次及以上")
    sportweek_cks=[ck_spw1,ck_spw2,ck_spw3,ck_spw4];bind_single_checkbox(sportweek_cks)
    ck_spt1=ft.Checkbox("＜20分钟");ck_spt2=ft.Checkbox("20–40分钟");ck_spt3=ft.Checkbox("40–60分钟");ck_spt4=ft.Checkbox("60分钟以上")
    sporttime_cks=[ck_spt1,ck_spt2,ck_spt3,ck_spt4];bind_single_checkbox(sporttime_cks)
    ck_run = ft.Checkbox(label="跑步/快走")
    ck_ball = ft.Checkbox(label="球类")
    ck_rope = ft.Checkbox(label="跳绳/体操")
    ck_swim = ft.Checkbox(label="游泳")
    ck_power = ft.Checkbox(label="力量训练")
    ck_nosport = ft.Checkbox(label="几乎不运动")
    sport_col = ft.Column([ck_run, ck_ball, ck_rope, ck_swim, ck_power, ck_nosport], spacing=4)
    ck_sta1=ft.Checkbox("＜3h");ck_sta2=ft.Checkbox("3–5h");ck_sta3=ft.Checkbox("5–7h");ck_sta4=ft.Checkbox("7h以上")
    static_cks=[ck_sta1,ck_sta2,ck_sta3,ck_sta4];bind_single_checkbox(static_cks)
    ck_wk1=ft.Checkbox("经常");ck_wk2=ft.Checkbox("一般");ck_wk3=ft.Checkbox("很少")
    walk_cks=[ck_wk1,ck_wk2,ck_wk3];bind_single_checkbox(walk_cks)

    # 睡眠（竖向）
    ck_be1=ft.Checkbox("21:30前");ck_be2=ft.Checkbox("21:30–22:30");ck_be3=ft.Checkbox("22:30–23:30");ck_be4=ft.Checkbox("23:30之后")
    bed_cks=[ck_be1,ck_be2,ck_be3,ck_be4];bind_single_checkbox(bed_cks)
    ck_sh1=ft.Checkbox("9h及以上");ck_sh2=ft.Checkbox("8–9h");ck_sh3=ft.Checkbox("7–8h");ck_sh4=ft.Checkbox("＜7h")
    sleeph_cks=[ck_sh1,ck_sh2,ck_sh3,ck_sh4];bind_single_checkbox(sleeph_cks)
    ck_sq1=ft.Checkbox("入睡快睡得香");ck_sq2=ft.Checkbox("偶尔失眠");ck_sq3=ft.Checkbox("经常熬夜浅眠")
    sleepq_cks=[ck_sq1,ck_sq2,ck_sq3];bind_single_checkbox(sleepq_cks)
    ck_st1=ft.Checkbox("从不");ck_st2=ft.Checkbox("偶尔");ck_st3=ft.Checkbox("经常")
    stress_cks=[ck_st1,ck_st2,ck_st3];bind_single_checkbox(stress_cks)

    # 身体状况（竖向）
    ck_en1=ft.Checkbox("精力充沛");ck_en2=ft.Checkbox("偶尔疲惫");ck_en3=ft.Checkbox("经常乏力犯困")
    energy_cks=[ck_en1,ck_en2,ck_en3];bind_single_checkbox(energy_cks)
    ck_sto1=ft.Checkbox("正常");ck_sto2=ft.Checkbox("腹胀消化不良");ck_sto3=ft.Checkbox("经常便秘");ck_sto4=ft.Checkbox("容易腹泻")
    stomach_cks=[ck_sto1,ck_sto2,ck_sto3,ck_sto4];bind_single_checkbox(stomach_cks)
    ck_wc1=ft.Checkbox("基本不变");ck_wc2=ft.Checkbox("明显上涨");ck_wc3=ft.Checkbox("明显下降")
    weightc_cks=[ck_wc1,ck_wc2,ck_wc3];bind_single_checkbox(weightc_cks)
    ck_ey1=ft.Checkbox("正常");ck_ey2=ft.Checkbox("轻度近视");ck_ey3=ft.Checkbox("中高度近视")
    eye_cks=[ck_ey1,ck_ey2,ck_ey3];bind_single_checkbox(eye_cks)
    ck_dizzy = ft.Checkbox(label="头晕")
    ck_pale = ft.Checkbox(label="面色苍白")
    ck_joint = ft.Checkbox(label="关节疼痛")
    ck_dry = ft.Checkbox(label="口干上火")
    ck_nosick = ft.Checkbox(label="无任何不适")
    ill_col = ft.Column([ck_dizzy, ck_pale, ck_joint, ck_dry, ck_nosick], spacing=4)

    # 需求（竖向）
    ck_1 = ft.Checkbox(label="均衡营养促发育")
    ck_2 = ft.Checkbox(label="减重控肥胖")
    ck_3 = ft.Checkbox(label="增重改善偏瘦")
    ck_4 = ft.Checkbox(label="纠正挑食偏食")
    ck_5 = ft.Checkbox(label="提升体能体育")
    ck_6 = ft.Checkbox(label="调理肠胃")
    ck_7 = ft.Checkbox(label="护眼增强抵抗力")
    ck_other = ft.Checkbox(label="其他")
    need_col = ft.Column([ck_1,ck_2,ck_3,ck_4,ck_5,ck_6,ck_7,ck_other], spacing=4)
    other_need = ft.TextField(label="其他需求填写")
    ck_lim1=ft.Checkbox("无");ck_lim2=ft.Checkbox("素食");ck_lim3=ft.Checkbox("食物过敏");ck_lim4=ft.Checkbox("忌口食物")
    limit_cks=[ck_lim1,ck_lim2,ck_lim3,ck_lim4]
    limit_detail = ft.TextField(label="过敏/忌口详情说明")

    report_text = ft.Text("报告将在此生成", selectable=True, size=13)
    loading_text = ft.Text("", color=ft.Colors.BLUE)

    def get_text(ck_list):
        arr = [x.label for x in ck_list if x.value]
        return arr[0] if arr else "未选"
    def get_mul(ck_list):
        arr = [x.label for x in ck_list if x.value]
        return "、".join(arr) if arr else "未勾选"

    def submit_all(e):
        errors = validate_inputs(age, height, weight, grade, sex_cks)
        if errors:
            page.show_snack_bar(ft.SnackBar(ft.Text("\n".join(errors)), bgcolor=ft.Colors.RED))
            return
        loading_text.value = "AI生成报告中..."
        page.update()
        try:
            info = f"""
【基础信息】性别：{get_text(sex_cks)}，年龄：{age.value}岁，年级：{grade.value}，身高：{height.value}cm，体重：{weight.value}kg
【家族病史】{get_mul([ck_fam_none,ck_fat,ck_hbp,ck_dm,ck_hlip,ck_gout])}
【膳食习惯】早餐：{get_text(breakfast_cks)}，蔬菜：{get_text(veg_cks)}，水果：{get_text(fruit_cks)}
【运动】{get_mul([ck_run,ck_ball,ck_rope,ck_swim,ck_power,ck_nosport])}
【睡眠】{get_text(bed_cks)}，{get_text(sleeph_cks)}
【身体】{get_text(energy_cks)}，{get_text(stomach_cks)}
【需求】{get_mul(limit_cks)}
            """
            res = get_nutrition_report(info)
            report_text.value = res
            loading_text.value = "✅ 生成完成！"
        except Exception as e:
            report_text.value = f"❌ 失败：{str(e)}"
            loading_text.value = "❌ 处理失败"
        page.update()

    # 🔥 核心：全部竖向布局，无任何横向并排
    content_col = ft.Column(spacing=8, controls=[
        ft.Text("青少年营养健康测评", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ft.Divider(),
        ft.Text("一、基础信息", size=16, weight=ft.FontWeight.BOLD),
        ft.Text("性别"), ft.Column(sex_cks, spacing=4),
        age, height, weight, grade,
        ft.Text("家族病史"), fam_col,
        ft.Divider(),
        ft.Text("二、膳食习惯", size=16, weight=ft.FontWeight.BOLD),
        ft.Text("早餐频率"), ft.Column(breakfast_cks, spacing=4),
        ft.Text("午餐规律"), ft.Column(lunch_cks, spacing=4),
        ft.Text("蔬菜"), ft.Column(veg_cks, spacing=4),
        ft.Text("水果"), ft.Column(fruit_cks, spacing=4),
        ft.Text("奶制品"), ft.Column(milk_cks, spacing=4),
        ft.Text("肉类"), ft.Column(meat_cks, spacing=4),
        ft.Text("鱼虾"), ft.Column(fish_cks, spacing=4),
        ft.Text("鸡蛋"), ft.Column(egg_cks, spacing=4),
        ft.Text("零食"), ft.Column(snack_cks, spacing=4),
        ft.Text("饮料"), ft.Column(drink_cks, spacing=4),
        ft.Text("油炸食品"), ft.Column(fry_cks, spacing=4),
        ft.Text("主食"), ft.Column(staple_cks, spacing=4),
        ft.Text("口味"), ft.Column(taste_cks, spacing=4),
        ft.Text("吃饭速度"), ft.Column(speed_cks, spacing=4),
        ft.Text("宵夜"), ft.Column(night_cks, spacing=4),
        ft.Divider(),
        ft.Text("三、运动", size=16, weight=ft.FontWeight.BOLD),
        ft.Text("运动次数"), ft.Column(sportweek_cks, spacing=4),
        ft.Text("运动时长"), ft.Column(sporttime_cks, spacing=4),
        ft.Text("运动类型"), sport_col,
        ft.Text("静态时长"), ft.Column(static_cks, spacing=4),
        ft.Text("日常活动"), ft.Column(walk_cks, spacing=4),
        ft.Divider(),
        ft.Text("四、睡眠", size=16, weight=ft.FontWeight.BOLD),
        ft.Text("上床时间"), ft.Column(bed_cks, spacing=4),
        ft.Text("睡眠时长"), ft.Column(sleeph_cks, spacing=4),
        ft.Text("睡眠质量"), ft.Column(sleepq_cks, spacing=4),
        ft.Text("压力"), ft.Column(stress_cks, spacing=4),
        ft.Divider(),
        ft.Text("五、身体状况", size=16, weight=ft.FontWeight.BOLD),
        ft.Text("精力"), ft.Column(energy_cks, spacing=4),
        ft.Text("肠胃"), ft.Column(stomach_cks, spacing=4),
        ft.Text("体重变化"), ft.Column(weightc_cks, spacing=4),
        ft.Text("视力"), ft.Column(eye_cks, spacing=4),
        ft.Text("不适症状"), ill_col,
        ft.Divider(),
        ft.Text("六、需求", size=16, weight=ft.FontWeight.BOLD),
        ft.Text("改善目标"), need_col,
        other_need,
        ft.Text("饮食禁忌"), ft.Column(limit_cks, spacing=4),
        limit_detail,
        ft.FilledButton("提交问卷，生成专属营养报告", on_click=submit_all, expand=True),
        loading_text,
        ft.Divider(),
        ft.Text("📄 个性化测评报告结果", size=16, weight=ft.FontWeight.BOLD),
        report_text
    ])
    page.add(content_col)

if __name__ == "__main__":
    ft.run(main)