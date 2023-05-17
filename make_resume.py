# -*- coding: utf-8 -*-
import re
import os

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Frame, Paragraph
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle


def replace_variables(l, data):
    # 再帰的にtempleteを探索しながら、"{{}}"と"$xxx"にマッチした文字列を置換する
    for idx, x in enumerate(l):
        if type(x) is str and x.startswith("$") and x[1:] in data:
            var = data[x[1:]]
            l[idx] = " " if var == "" else var
        elif type(x) is str and re.match(r"\{\{(.+?)\}\}", x):
            key = re.findall(r"\{\{(.+?)\}\}", x)[0]
            if key in data:
                history = data[key]
                l[idx] = [list(x.values()) for x in history]
            else:
                l[idx] = [""]
        elif type(x) is list:
            replace_variables(x, data)
    return


def make_resume(output_file, data, font_path, photo_path=None):
    # 履歴書作成
    templete = [
        "履  歴  書",
        "$date",
        [["写真を貼る位置\n1. 縦36-40mm\n     横24-30mm\n2. 本人単身胸から上\n3. 裏面にのりづけ\n4. 裏面に氏名記入"]],
        [["ふりがな", "$name_kana"], ["氏名", "$name"]],
        [["生年月日", "$birth_day", "性別", "$gender"]],
        [
            ["ふりがな", "$address_kana1"],
            ["現住所", "$address_zip1"],
            ["", "$address1"],
            ["ふりがな", "$address_kana2"],
            ["連絡先", "$address_zip2"],
            ["", "$address2"],
        ],
        [
            ["Tell"],
            ["$tel1"],
            ["E-mail"],
            ["$email1"],
            ["Tell"],
            ["$tel2"],
            ["E-mail"],
            ["$email2"],
        ],
        [["年", "月", "学歴・職歴(各項目ごとにまとめて書く)"]],
        [["", "", "学　歴"]],
        "{{education}}",
        [["", "", "職　歴"]],
        "{{experience}}",
        [["", "", "以上"]],
        [["年", "月", "免許・資格"]],
        "{{licences}}",
        [
            ["通勤時間", "扶養家族", "", "配偶者", "配偶者の扶養義務"],
            [
                "$commuting_time",
                "（配偶者を除く）",
                "$dependents",
                "$spouse",
                "$supporting_spouse",
            ],
        ],
        ["趣味・特技", "$hobby"],
        ["志望動機", "$motivation"],
        ["本人希望", "$request"],
    ]
    replace_variables(templete, data)

    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("myfont", font_path))
        font = "myfont"
    else:
        font = "HeiseiKakuGo-W5"  # デフォルトの日本語フォント(平成角ゴシック体W5)

    FONTSIZE_content = 11
    FONTSIZE_label = 8

    # テキストボックス用のスタイル
    title_style = ParagraphStyle(
        name="Heading1", fontName=font, fontSize=FONTSIZE_label, leading=20
    )
    content_style = ParagraphStyle(
        name="Normal", fontName=font, fontSize=FONTSIZE_content
    )

    pdf_canvas = canvas.Canvas(output_file)

    # (1)履歴書 タイトル
    font_size = 16
    pdf_canvas.setFont(font, font_size)
    pdf_canvas.drawString(21 * mm, 270 * mm, templete[0])

    # (2)作成日
    pdf_canvas.setFont(font, FONTSIZE_label)
    pdf_canvas.drawString(116 * mm, 270 * mm, templete[1])

    # (3)証明写真
    # tableを作成
    table = Table(templete[2], colWidths=(30 * mm), rowHeights=(40 * mm))
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (0, 0), font, FONTSIZE_label),
                ("BOX", (0, 0), (0, 0), 1, colors.black),
                ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 155 * mm, 235 * mm)
    table.drawOn(pdf_canvas, 155 * mm, 235 * mm)

    if photo_path and os.path.exists(photo_path):
        pdf_canvas.drawImage(photo_path, 155 * mm, 235 * mm, 30 * mm, 40 * mm)

    # (4)プロフィール
    table = Table(
        templete[3],
        colWidths=(20 * mm, 110 * mm),
        rowHeights=(7 * mm, 20 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (1, 1), font, FONTSIZE_label),
                ("BOX", (0, 0), (1, 1), 1, colors.black),
                ("LINEABOVE", (0, 0), (1, 1), 1, colors.black),
                ("VALIGN", (0, 0), (1, 1), "MIDDLE"),
                ("VALIGN", (0, 1), (0, 1), "TOP"),
                ("FONT", (1, 1), (1, 1), font, 14),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 20 * mm, 242 * mm)
    table.drawOn(pdf_canvas, 20 * mm, 242 * mm)

    # (5) 生年月日・性別
    table = Table(
        templete[4],
        colWidths=(20 * mm, 75 * mm, 15 * mm, 20 * mm),
        rowHeights=(10 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (3, 0), font, FONTSIZE_label),
                ("BOX", (0, 0), (3, 0), 1, colors.black),
                ("INNERGRID", (0, 0), (3, 0), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONT", (1, 0), (1, 0), font, FONTSIZE_content),
                ("FONT", (3, 0), (3, 0), font, FONTSIZE_content),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 20 * mm, 232 * mm)
    table.drawOn(pdf_canvas, 20 * mm, 232 * mm)

    # (6)住所
    input_table = templete[5]
    input_table[2][1] = Paragraph(input_table[2][1], content_style)
    input_table[5][1] = Paragraph(input_table[5][1], content_style)

    table = Table(
        input_table,
        colWidths=(14 * mm, 116 * mm),
        rowHeights=(6 * mm, 6 * mm, 15 * mm, 6 * mm, 6 * mm, 15 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (1, 5), font, FONTSIZE_label),
                ("BOX", (0, 0), (1, 5), 1, colors.black),
                ("FONT", (1, 2), (1, 2), font, FONTSIZE_content),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONT", (1, 5), (1, 5), font, FONTSIZE_content),
                ("LINEBELOW", (0, 0), (1, 0), 1, colors.black),
                ("LINEBELOW", (0, 2), (1, 2), 1, colors.black),
                ("LINEBELOW", (0, 3), (1, 3), 1, colors.black),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 20 * mm, 178 * mm)
    table.drawOn(pdf_canvas, 20 * mm, 178 * mm)

    # (7)電話・メール
    table = Table(templete[6], colWidths=(40 * mm), rowHeights=(6.75 * mm))
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), font, FONTSIZE_label),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("LINEBELOW", (0, 1), (0, 1), 1, colors.black),
                ("LINEBELOW", (0, 3), (0, 3), 1, colors.black),
                ("LINEBELOW", (0, 5), (0, 5), 1, colors.black),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 150 * mm, 178 * mm)
    table.drawOn(pdf_canvas, 150 * mm, 178 * mm)

    # (7)学歴・職種
    input_row = len(templete[9]) + len(templete[11]) + 3

    input_table = (
        templete[7]
        + templete[8]
        + templete[9]
        + templete[10]
        + templete[11]
        + templete[12]
        + [[" ", " ", " "] for _ in range(20 - input_row)]
    )

    table = Table(
        input_table, colWidths=(25 * mm, 14 * mm, 131 * mm), rowHeights=7.5 * mm
    )
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), font, FONTSIZE_content),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (1, -1), "CENTER"),
                ("ALIGN", (0, 0), (3, 1), "CENTER"),
                (
                    "ALIGN",
                    (2, len(templete[9]) + 2),
                    (2, len(templete[9]) + 2),
                    "CENTER",
                ),
                (
                    "ALIGN",
                    (2, len(templete[9]) + len(templete[11]) + 3),
                    (2, len(templete[9]) + len(templete[11]) + 3),
                    "RIGHT",
                ),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 20 * mm, 20 * mm)
    table.drawOn(pdf_canvas, 20 * mm, 20 * mm)

    # 1枚目終了
    pdf_canvas.showPage()

    # (8)免許・資格
    input_row = len(templete[13]) + len(templete[14]) + 1
    input_table = (
        templete[13] + templete[14] + [[" ", " ", " "] for _ in range(8 - input_row)]
    )
    table = Table(
        input_table, colWidths=(25 * mm, 14 * mm, 131 * mm), rowHeights=7.5 * mm
    )
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), font, FONTSIZE_content),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (1, -1), "CENTER"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 20 * mm, 217 * mm)
    table.drawOn(pdf_canvas, 20 * mm, 217 * mm)

    # (9)通勤時間・扶養
    table = Table(
        templete[15],
        colWidths=(42.5 * mm, 30 * mm, 12.5 * mm, 42.5 * mm, 42.5 * mm),
        rowHeights=(5 * mm, 14 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, 0), font, FONTSIZE_label),
                ("FONT", (0, 1), (-1, 1), font, FONTSIZE_content),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("LINEAFTER", (0, 0), (0, 1), 1, colors.black),
                ("LINEAFTER", (2, 0), (-1, 1), 1, colors.black),
                ("SPAN", (1, 0), (2, 0)),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONT", (1, 1), (1, 1), font, FONTSIZE_label),
            ]
        )
    )
    table.wrapOn(pdf_canvas, 20 * mm, 194 * mm)
    table.drawOn(pdf_canvas, 20 * mm, 194 * mm)

    # (10)趣味・特技
    f = Frame(20 * mm, 136 * mm, 170 * mm, 54 * mm, showBoundary=1)
    title_paragraph = Paragraph(templete[16][0], title_style)
    content_paragraph = Paragraph(templete[16][1], content_style)
    story = [title_paragraph, content_paragraph]

    f.addFromList(story, pdf_canvas)

    # (11)志望動機
    f = Frame(20 * mm, 78 * mm, 170 * mm, 54 * mm, showBoundary=1)
    title_paragraph = Paragraph(templete[17][0], title_style)
    content_paragraph = Paragraph(templete[17][1], content_style)
    story = [title_paragraph, content_paragraph]

    f.addFromList(story, pdf_canvas)

    # (12)本人希望
    f = Frame(20 * mm, 20 * mm, 170 * mm, 54 * mm, showBoundary=1)
    title_paragraph = Paragraph(templete[18][0], title_style)
    content_paragraph = Paragraph(templete[18][1], content_style)
    story = [title_paragraph, content_paragraph]

    f.addFromList(story, pdf_canvas)

    # 　終了
    pdf_canvas.showPage()
    pdf_canvas.save()
