import os
import subprocess
import tempfile
import math
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
global_submissions = []

problems_db = [
    { 
        "id": 1, "name": "1. Rẽ nhánh: Chẵn/Lẻ/Âm/Dương", 
        "desc": "Nhập vào số nguyên n. In ra <code>ZERO</code> nếu bằng 0, ngược lại in <code>EVEN</code> nếu chẵn hoặc <code>ODD</code> nếu lẻ.", 
        "sampleIn": "-4", "sampleOut": "EVEN", 
        "tests": [{"input": f"{n}\n", "expected": f"{'ZERO' if n == 0 else ('EVEN' if n % 2 == 0 else 'ODD')}\n"} for n in [i-5 for i in range(1, 11)]] 
    },
    { 
        "id": 2, "name": "2. Vòng lặp: Tính tổng 1 đến N", 
        "desc": "Nhập số nguyên dương n. Tính và in ra tổng S = 1 + 2 + ... + n.", 
        "sampleIn": "4", "sampleOut": "10", 
        "tests": [{"input": f"{n}\n", "expected": f"{n * (n + 1) // 2}\n"} for n in [i*2 for i in range(1, 11)]] 
    },
    { 
        "id": 3, "name": "3. Số nguyên tố (Cơ bản)", 
        "desc": "Nhập số nguyên n. Kiểm tra xem n có phải số nguyên tố không. In ra <code>YES</code> hoặc <code>NO</code>.", 
        "sampleIn": "7", "sampleOut": "YES", 
        "tests": [{"input": f"{n}\n", "expected": f"{'YES\n' if (n > 1 and all(n % d != 0 for d in range(2, int(n**0.5)+1))) else 'NO\n'}"} for n in [i+1 for i in range(1, 11)]] 
    },
    { 
        "id": 4, "name": "4. Số chính phương (Cơ bản)", 
        "desc": "Nhập số nguyên n. Kiểm tra xem n có phải là số chính phương hay không. In ra <code>YES</code> hoặc <code>NO</code>.", 
        "sampleIn": "9", "sampleOut": "YES", 
        "tests": [{"input": f"{n}\n", "expected": f"{'YES\n' if int(n**0.5)**2 == n else 'NO\n'}"} for n in [i*i for i in range(1, 11)]] 
    },
    { 
        "id": 5, "name": "5. Tổng hợp: Tìm Max 3 số", 
        "desc": "Nhập 3 số nguyên a, b, c trên một dòng. In ra giá trị lớn nhất.", 
        "sampleIn": "3 9 5", "sampleOut": "9", 
        "tests": [{"input": f"{i} {i*2} {i+3}\n", "expected": f"{max(i, i*2, i+3)}\n"} for i in range(1, 11)] 
    },
    { 
        "id": 6, "name": "6. Vòng lặp nâng cấp: Đếm chia hết cho 3", 
        "desc": "Nhập n. Đếm số lượng các số chia hết cho 3 trong khoảng từ 1 đến n.", 
        "sampleIn": "10", "sampleOut": "3", 
        "tests": [{"input": f"{n}\n", "expected": f"{sum(1 for x in range(1, n+1) if x % 3 == 0)}\n"} for n in [i*3 for i in range(1, 11)]] 
    },
    { 
        "id": 7, "name": "7. Tổng chữ số nâng cấp", 
        "desc": "Nhập số nguyên n. Tính tổng tất cả các chữ số của n.", 
        "sampleIn": "123", "sampleOut": "6", 
        "tests": [{"input": f"{n}\n", "expected": f"{sum(int(c) for c in str(n))}\n"} for n in [i*15 for i in range(1, 11)]] 
    },
    { 
        "id": 8, "name": "8. Số nguyên tố nâng cấp", 
        "desc": "Kiểm tra số nguyên tố với các test case mở rộng. In ra <code>YES</code> hoặc <code>NO</code>.", 
        "sampleIn": "17", "sampleOut": "YES", 
        "tests": [{"input": f"{v}\n", "expected": f"{'YES\n' if (v > 1 and all(v % d != 0 for d in range(2, int(v**0.5)+1))) else 'NO\n'}"} for v in [1, 4, 13, 17, 20, 29, 30, 97, 100, 101]] 
    },
    { 
        "id": 9, "name": "9. Số chính phương nâng cấp", 
        "desc": "Kiểm tra số chính phương với các giá trị lớn hơn. In ra <code>YES</code> hoặc <code>NO</code>.", 
        "sampleIn": "36", "sampleOut": "YES", 
        "tests": [{"input": f"{n}\n", "expected": f"{'YES\n' if int(n**0.5)**2 == n else 'NO\n'}"} for n in [(i+5)**2 for i in range(1, 11)]] 
    },
    { 
        "id": 10, "name": "10. UCLN (GCD) hai số", 
        "desc": "Nhập hai số nguyên a và b trên một dòng. Tìm và in ra ước chung lớn nhất.", 
        "sampleIn": "12 18", "sampleOut": "6", 
        "tests": [{"input": f"{i*4} {i*6}\n", "expected": f"{math.gcd(i*4, i*6)}\n"} for i in range(1, 11)] 
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <title>HuyOJ - Quản Lý & Chấm Bài C++</title>
    <style>
        :root {
            --bg-color: #1e1e1e; --panel-bg: #252526; --text-color: #d4d4d4;
            --border-color: #333; --header-bg: #2d2d2d; --accent: #007acc; --hover-bg: #383838;
        }
        [data-theme="light"] {
            --bg-color: #f3f3f3; --panel-bg: #ffffff; --text-color: #333333;
            --border-color: #dddddd; --header-bg: #e1e1e1; --accent: #005fb8; --hover-bg: #eaeaea;
        }
        body { font-family: sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 15px; }
        .container { max-width: 1400px; margin: auto; background: var(--panel-bg); padding: 20px; border-radius: 8px; border: 1px solid var(--border-color); }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
        h1 { color: #4ec9b0; margin: 0; font-size: 22px; cursor: pointer; }
        .nav-tabs, .controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .tab-btn, .ctrl-btn { background: var(--header-bg); border: 1px solid var(--border-color); color: var(--text-color); padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 13px; }
        .tab-btn.active, .ctrl-btn:hover { background: var(--accent); color: white; border-color: var(--accent); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .layout-prob { display: flex; gap: 20px; }
        .sidebar-prob { width: 320px; border-right: 1px solid var(--border-color); padding-right: 15px; max-height: 550px; overflow-y: auto; }
        .main-prob { flex: 1; display: flex; flex-direction: column; }
        .btn-prob { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 10px 12px; margin-bottom: 8px; background: var(--header-bg); border: 1px solid var(--border-color); color: var(--text-color); cursor: pointer; font-weight: 600; border-radius: 4px; text-align: left; font-size: 13px; }
        .btn-prob:hover { background: var(--hover-bg); }
        .btn-prob.active { background: var(--accent); color: white; }
        
        .problem-card { background: var(--bg-color); border: 1px solid var(--border-color); padding: 20px; border-radius: 6px; }
        .io-box { background: var(--header-bg); border: 1px solid var(--border-color); padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; white-space: pre-wrap; font-size: 13px; }
        
        .ide-layout { display: flex; flex-direction: column; gap: 15px; }
        .ide-top-bar { display: flex; justify-content: space-between; align-items: center; background: var(--header-bg); padding: 10px 15px; border-radius: 6px; border: 1px solid var(--border-color); }
        
        .code-editor {
            width: 100%; height: 420px; background-color: #1e1e1e; color: #d4d4d4;
            font-family: 'Courier New', Courier, monospace; font-size: 14px; line-height: 1.5;
            padding: 15px; border: 1px solid var(--border-color); border-radius: 6px;
            resize: vertical; outline: none; box-sizing: border-box; tab-size: 4;
        }
        [data-theme="light"] .code-editor { background-color: #ffffff; color: #000000; }

        .submit-btn { background: #2ea043; color: white; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; border-radius: 4px; font-size: 14px; }
        .submit-btn:hover { background: #2c974b; }
        .danger-btn { background: #da3633; color: white; border: none; padding: 6px 12px; font-weight: bold; cursor: pointer; border-radius: 4px; font-size: 12px; }
        .danger-btn:hover { background: #b31d1c; }
        
        .test-results-container { margin-top: 15px; display: flex; flex-direction: column; gap: 10px; padding-bottom: 20px; }
        .test-case-card { background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 6px; overflow: hidden; }
        .test-case-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; background: var(--header-bg); cursor: pointer; font-weight: bold; font-size: 13px; user-select: none; }
        .test-case-header:hover { background: var(--hover-bg); }
        .test-case-body { padding: 15px; font-family: monospace; font-size: 13px; display: none; border-top: 1px solid var(--border-color); background: var(--panel-bg); line-height: 1.6; }
        
        .badge { padding: 3px 8px; font-size: 11px; font-weight: bold; border-radius: 3px; color: #fff; }
        .badge.AC { background: #238636; } .badge.WA { background: #da3633; } .badge.TLE { background: #d29922; color: #000; } .badge.RTE { background: #db6d28; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: var(--panel-bg); border: 1px solid var(--border-color); }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 13px; }
        th { background: var(--header-bg); color: #4ec9b0; }

        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-weight: bold; margin-bottom: 5px; font-size: 13px; color: #4ec9b0; }
        .form-control { width: 100%; padding: 8px 12px; background: var(--bg-color); border: 1px solid var(--border-color); color: var(--text-color); border-radius: 4px; box-sizing: border-box; font-size: 13px; }
        
        .generator-box { background: var(--header-bg); border: 1px solid var(--border-color); padding: 12px; border-radius: 6px; margin-bottom: 15px; }
        .clickable-row { cursor: pointer; }
        .clickable-row:hover { background: var(--hover-bg); }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1 onclick="goHome()">⚡ HuyOJ - <span data-i18n="sysTitle">Hệ Thống Chấm Bài C++</span></h1>
        <div class="nav-tabs">
            <button class="tab-btn active" id="btn-tab-list" onclick="switchMainTab('list')">📚 <span data-i18n="tabList">Danh sách bài tập</span></button>
            <button class="tab-btn" id="btn-tab-admin-add" onclick="switchMainTab('admin-add')">➕ <span data-i18n="tabAdd">Thêm bài tập</span></button>
            <button class="tab-btn" id="btn-tab-admin-manage" onclick="switchMainTab('admin-manage')">⚙️ <span data-i18n="tabManage">Quản lý & Sửa bài</span></button>
            <button class="tab-btn" id="btn-tab-admin" onclick="switchMainTab('admin')">🛡️ <span data-i18n="tabHistory">Lịch sử Chấm</span></button>
        </div>
        <!-- Đã tách ra 4 nút điều khiển riêng biệt -->
        <div class="controls">
            <button class="ctrl-btn" id="btn-lang" onclick="toggleLanguage()">🌐 VN / EN</button>
            <button class="ctrl-btn" id="btn-theme" onclick="toggleTheme()">☀️ <span data-i18n="themeBtn">Sáng/Tối</span></button>
        </div>
    </div>

    <!-- TAB 1: DANH SÁCH BÀI TẬP -->
    <div id="content-list" class="tab-content active">
        <div class="layout-prob">
            <div class="sidebar-prob" id="prob-sidebar">
                <h3 style='margin-top:0; font-size:14px;' data-i18n="loading">Đang tải dữ liệu...</h3>
            </div>
            <div class="main-prob">
                <div class="problem-card" id="problem-detail-card">
                    <h2 id="d-title" style="margin-top:0; color:#4ec9b0;" data-i18n="selectProbPrompt">Chọn một bài tập bên trái</h2>
                    <div id="d-desc" data-i18n="selectProbDesc">Vui lòng chọn bài tập để xem đề bài chi tiết, input/output mẫu.</div>
                    <div id="d-io-section" style="display:none;">
                        <h4 data-i18n="sampleInTitle">Ví dụ Input mẫu:</h4>
                        <div class="io-box" id="d-sample-in"></div>
                        <h4 data-i18n="sampleOutTitle">Ví dụ Output mẫu:</h4>
                        <div class="io-box" id="d-sample-out"></div>
                        <button class="submit-btn" style="margin-top: 10px;" onclick="goToIde(currentId)">✍️ Nạp Bài</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: MÀN HÌNH VIẾT CODE -->
    <div id="content-ide" class="tab-content">
        <div class="ide-layout">
            <div class="ide-top-bar">
                <div>
                    <button class="ctrl-btn" onclick="goHome()">⬅ <span data-i18n="backBtn">Quay lại danh sách</span></button>
                    <span id="ide-prob-title" style="margin-left: 15px; font-weight: bold; color: #4ec9b0; font-size: 15px;"></span>
                </div>
                <div>
                    <button class="submit-btn" onclick="submitCode()"><span data-i18n="submitBtn">Nộp bài C++</span></button>
                </div>
            </div>
            
            <textarea id="code-textarea" class="code-editor" spellcheck="false" placeholder="Viết mã nguồn C++ tại đây..." onkeydown="handleCodeIndent(event)"></textarea>
            <div id="summary" style="font-weight: bold; color: #4ec9b0; font-size: 14px;"></div>
            <div class="test-results-container" id="test-results-list"></div>
        </div>
    </div>

    <!-- TAB 3: THÊM BÀI TẬP -->
    <div id="content-admin-add" class="tab-content">
        <h2 style="color: #4ec9b0; margin-top: 0;" data-i18n="addTitle">🛠️ Thêm bài tập mới (Dành cho mọi người)</h2>
        <div class="problem-card" style="max-width: 850px;">
            <div class="form-group">
                <label data-i18n="lblName">Tên bài tập:</label>
                <input type="text" id="new-name" class="form-control" placeholder="Ví dụ: 11. In lời chào">
            </div>
            <div class="form-group">
                <label data-i18n="lblDesc">Mô tả đề bài:</label>
                <textarea id="new-desc" class="form-control" rows="4" placeholder="Nhập vào tên. In ra Xin chào kèm theo tên."></textarea>
            </div>
            <div style="display: flex; gap: 15px;">
                <div class="form-group" style="flex: 1;">
                    <label data-i18n="lblSampleIn">Input mẫu (Sample In):</label>
                    <input type="text" id="new-sample-in" class="form-control" placeholder="Huy">
                </div>
                <div class="form-group" style="flex: 1;">
                    <label data-i18n="lblSampleOut">Output mẫu (Sample Out):</label>
                    <input type="text" id="new-sample-out" class="form-control" placeholder="Xin chào Huy">
                </div>
            </div>

            <div class="generator-box">
                <label style="color: #4ec9b0; font-weight: bold; font-size: 14px; margin-bottom: 8px; display:block;" data-i18n="lblGenTitle">🪄 Trợ lý tạo Test Cases tự động:</label>
                <div style="display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
                    <button type="button" class="ctrl-btn" onclick="autoFillGreetingTemplate()" data-i18n="btnGen1">👉 Mẫu: In chuỗi cố định</button>
                    <button type="button" class="ctrl-btn" onclick="autoFillSumTemplate()" data-i18n="btnGen2">👉 Mẫu: Tính tổng 1 đến N</button>
                </div>
                <textarea id="new-generator" class="form-control" rows="4" placeholder="tests = [{'input': 'Huy\\n', 'expected': 'Xin chào Huy\\n'}]"></textarea>
            </div>

            <button class="submit-btn" onclick="addNewProblem()" data-i18n="btnCreate">✨ Tạo bài tập mới</button>
            <div id="add-status" style="margin-top: 10px; font-weight: bold;"></div>
        </div>
    </div>

    <!-- TAB 4: QUẢN LÝ & SỬA BÀI TẬP -->
    <div id="content-admin-manage" class="tab-content">
        <h2 style="color: #4ec9b0; margin-top: 0;" data-i18n="manageTitle">⚙️ Quản lý, Chỉnh sửa bài tập & Test Cases</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="width: 300px; min-width: 250px;">
                <label style="font-weight: bold; color: #4ec9b0; display:block; margin-bottom:5px;" data-i18n="lblSelectEdit">Chọn bài cần sửa:</label>
                <select id="manage-select-prob" class="form-control" size="15" onchange="loadProblemForEdit()" style="height: 400px; font-family: monospace;"></select>
            </div>
            <div style="flex: 1; min-width: 300px;" class="problem-card" id="edit-form-container">
                <input type="hidden" id="edit-id">
                <div class="form-group">
                    <label data-i18n="lblName">Tên bài tập:</label>
                    <input type="text" id="edit-name" class="form-control">
                </div>
                <div class="form-group">
                    <label data-i18n="lblDesc">Mô tả đề bài:</label>
                    <textarea id="edit-desc" class="form-control" rows="3"></textarea>
                </div>
                <div style="display: flex; gap: 15px;">
                    <div class="form-group" style="flex: 1;">
                        <label data-i18n="lblSampleIn">Input mẫu:</label>
                        <input type="text" id="edit-sample-in" class="form-control">
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label data-i18n="lblSampleOut">Output mẫu:</label>
                        <input type="text" id="edit-sample-out" class="form-control">
                    </div>
                </div>
                <div class="form-group">
                    <label data-i18n="lblTestsJSON">Bộ Test Cases hiện tại (JSON):</label>
                    <textarea id="edit-tests" class="form-control" rows="6" style="font-family: monospace; font-size: 12px;"></textarea>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button class="submit-btn" onclick="updateProblem()" data-i18n="btnSave">💾 Lưu thay đổi</button>
                    <button class="danger-btn" onclick="deleteProblem()" data-i18n="btnDelete">🗑️ Xóa bài tập này</button>
                </div>
                <div id="edit-status" style="margin-top: 10px; font-weight: bold;"></div>
            </div>
        </div>
    </div>

    <!-- TAB 5: LỊCH SỬ CHẤM BÀI -->
    <div id="content-admin" class="tab-content">
        <h2 style="color: #dcdcaa; margin-top: 0;" data-i18n="historyTitle">Lịch sử nộp bài toàn hệ thống</h2>
        <p style="font-size: 13px; color: var(--text-color); opacity: 0.8;" data-i18n="historySub">💡 Bấm vào một dòng trong bảng để xem chi tiết code và các test case của lần nộp đó.</p>
        <button class="ctrl-btn" onclick="loadAdminLogs()" style="margin-bottom: 10px;">🔄 <span data-i18n="btnRefresh">Làm mới</span></button>
        <table>
            <thead>
                <tr>
                    <th data-i18n="thNo">STT</th>
                    <th data-i18n="thTime">Thời gian</th>
                    <th data-i18n="thProblem">Bài tập</th>
                    <th data-i18n="thDetail">Chi tiết</th>
                    <th data-i18n="thStatus">Trạng thái</th>
                </tr>
            </thead>
            <tbody id="admin-log-body">
                <tr><td colspan="5" style="text-align: center;" data-i18n="noData">Chưa có dữ liệu.</td></tr>
            </tbody>
        </table>

        <!-- Khung xem chi tiết bài nộp trong Lịch sử (Bài nào ra bài nấy, độc lập hoàn toàn) -->
        <div id="submission-detail-container" style="margin-top: 25px; display: none;" class="problem-card">
            <h3 style="color: #4ec9b0; margin-top: 0;" data-i18n="subDetailHeader">📄 Chi tiết bài nộp đã chọn</h3>
            <div class="form-group">
                <label data-i18n="subDetailCode">Mã nguồn C++ đã nộp:</label>
                <textarea id="log-view-code" class="code-editor" style="height: 250px; background: var(--bg-color);" readonly></textarea>
            </div>
            <h4 data-i18n="subDetailTests">Kết quả các Test Cases trong lần nộp này:</h4>
            <div id="log-view-tests" class="test-results-container"></div>
        </div>
    </div>
</div>

<script>
    // Mặc định luôn là 'light' (Sáng) và 'vi' (Tiếng Việt) và khôi phục từ localStorage nếu có
    let currentTheme = localStorage.getItem('theme') || 'light';
    let currentLang = localStorage.getItem('language') || 'vi';
    let currentId = 1;
    let problems = [];
    let allLogs = [];

    const i18n = {
        vi: {
            sysTitle: "Hệ Thống Chấm Bài C++",
            tabList: "Danh sách bài tập",
            tabAdd: "Thêm bài tập",
            tabManage: "Quản lý & Sửa bài",
            tabHistory: "Lịch sử Chấm",
            themeBtn: "Sáng/Tối",
            loading: "Đang tải dữ liệu...",
            selectProbPrompt: "Chọn một bài tập bên trái",
            selectProbDesc: "Vui lòng chọn bài tập để xem đề bài chi tiết, input/output mẫu.",
            sampleInTitle: "Ví dụ Input mẫu:",
            sampleOutTitle: "Ví dụ Output mẫu:",
            writeCodeBtn: "Viết code giải bài này",
            backBtn: "Quay lại danh sách",
            submitBtn: "Nộp bài C++",
            addTitle: "🛠️ Thêm bài tập mới (Dành cho mọi người)",
            lblName: "Tên bài tập:",
            lblDesc: "Mô tả đề bài:",
            lblSampleIn: "Input mẫu (Sample In):",
            lblSampleOut: "Output mẫu (Sample Out):",
            lblGenTitle: "🪄 Trợ lý tạo Test Cases tự động:",
            btnGen1: "👉 Mẫu: In chuỗi cố định",
            btnGen2: "👉 Mẫu: Tính tổng 1 đến N",
            btnCreate: "✨ Tạo bài tập mới",
            manageTitle: "⚙️ Quản lý, Chỉnh sửa bài tập & Test Cases",
            lblSelectEdit: "Chọn bài cần sửa:",
            lblTestsJSON: "Bộ Test Cases hiện tại (JSON):",
            btnSave: "💾 Lưu thay đổi",
            btnDelete: "🗑️ Xóa bài tập này",
            historyTitle: "Lịch sử nộp bài toàn hệ thống",
            historySub: "💡 Bấm vào một dòng trong bảng để xem chi tiết code và các test case của lần nộp đó.",
            btnRefresh: "Làm mới",
            thNo: "STT",
            thTime: "Thời gian",
            thProblem: "Bài tập",
            thDetail: "Chi tiết",
            thStatus: "Trạng thái",
            noData: "Chưa có dữ liệu.",
            subDetailHeader: "📄 Chi tiết bài nộp đã chọn",
            subDetailCode: "Mã nguồn C++ đã nộp:",
            subDetailTests: "Kết quả các Test Cases trong lần nộp này:"
        },
        en: {
            sysTitle: "C++ Online Judge System",
            tabList: "Problem List",
            tabAdd: "Add Problem",
            tabManage: "Manage Problems",
            tabHistory: "Submission History",
            themeBtn: "Light/Dark",
            loading: "Loading data...",
            selectProbPrompt: "Select a problem from the left",
            selectProbDesc: "Please choose a problem to view detailed description and sample I/O.",
            sampleInTitle: "Sample Input:",
            sampleOutTitle: "Sample Output:",
            writeCodeBtn: "Write code to solve this",
            backBtn: "Back to list",
            submitBtn: "Submit C++ Code",
            addTitle: "🛠️ Add New Problem",
            lblName: "Problem Name:",
            lblDesc: "Description:",
            lblSampleIn: "Sample Input:",
            lblSampleOut: "Sample Output:",
            lblGenTitle: "🪄 Test Case Generator Assistant:",
            btnGen1: "👉 Template: Print fixed string",
            btnGen2: "👉 Template: Sum 1 to N",
            btnCreate: "✨ Create Problem",
            manageTitle: "⚙️ Manage & Edit Problems & Test Cases",
            lblSelectEdit: "Select problem to edit:",
            lblTestsJSON: "Current Test Cases (JSON):",
            btnSave: "💾 Save Changes",
            btnDelete: "🗑️ Delete Problem",
            historyTitle: "System Submission History",
            historySub: "💡 Click any row in the table to view the exact code and test cases for that submission.",
            btnRefresh: "Refresh",
            thNo: "No.",
            thTime: "Time",
            thProblem: "Problem",
            thDetail: "Detail",
            thStatus: "Status",
            noData: "No data available.",
            subDetailHeader: "📄 Selected Submission Details",
            subDetailCode: "Submitted C++ Code:",
            subDetailTests: "Test Cases Result for this Submission:"
        }
    };

    function toggleLanguage() {
        currentLang = currentLang === 'vi' ? 'en' : 'vi';
        localStorage.setItem('language', currentLang);
        updateTexts();
    }

    function updateTexts() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (i18n[currentLang][key]) {
                el.innerText = i18n[currentLang][key];
            }
        });
    }

    function toggleTheme() {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
    }

    // Khởi tạo giao diện và ngôn ngữ từ localStorage ngay khi tải trang
    document.addEventListener("DOMContentLoaded", () => {
        document.documentElement.setAttribute('data-theme', currentTheme);
        updateTexts();
        fetchProblems();
    });

    function handleCodeIndent(e) {
        const textarea = e.target;
        let code = textarea.value;
        let selStart = textarea.selectionStart;
        let selEnd = textarea.selectionEnd;

        if (e.key === 'Tab') {
            e.preventDefault();
            textarea.value = code.substring(0, selStart) + "    " + code.substring(selEnd);
            textarea.selectionStart = textarea.selectionEnd = selStart + 4;
            return;
        }

        if (e.key === 'Enter') {
            e.preventDefault();
            let lineStart = code.lastIndexOf("\\n", selStart - 1) + 1;
            let currentLine = code.substring(lineStart, selStart);
            
            let match = currentLine.match(/^([ \\t]*)/);
            let indent = match ? match[1] : "";
            
            let trimmedLine = currentLine.trim();
            if (trimmedLine.endsWith('{')) {
                indent += "    ";
            }

            let insertion = "\\n" + indent;
            textarea.value = code.substring(0, selStart) + insertion + code.substring(selEnd);
            textarea.selectionStart = textarea.selectionEnd = selStart + insertion.length;
            textarea.scrollTop = textarea.scrollTop;
        }
    }

    function autoFillGreetingTemplate() {
        document.getElementById('new-generator').value = `tests = []
names = ["An", "Bình", "Châu", "Dũng", "Huy"]
for name in names:
    tests.append({
        "input": name + "\\\\n",
        "expected": "Xin chào " + name + "\\\\n"
    })`;
    }

    function autoFillSumTemplate() {
        document.getElementById('new-generator').value = `tests = []
for n in range(1, 11):
    s = n * (n + 1) // 2
    tests.append({
        "input": str(n) + "\\\\n",
        "expected": str(s) + "\\\\n"
    })`;
    }

    async function fetchProblems() {
        try {
            let res = await fetch('/api/problems');
            if (!res.ok) throw new Error("Lỗi Server " + res.status);
            
            problems = await res.json();
            if(problems.length > 0 && !problems.some(p => p.id === currentId)) {
                currentId = problems[0].id;
            }
            renderSidebar();
            loadProblemDetail();
        } catch(e) {
            console.error(e);
            document.getElementById("prob-sidebar").innerHTML = "<h3 style='color:#da3633; margin-top:0;'>❌ Lỗi tải bài tập.</h3>";
        }
    }

    function switchMainTab(tabKey) {
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        
        if (tabKey === 'list') {
            document.getElementById('content-list').classList.add('active');
            document.getElementById('btn-tab-list').classList.add('active');
            fetchProblems();
        } else if (tabKey === 'admin-add') {
            document.getElementById('content-admin-add').classList.add('active');
            document.getElementById('btn-tab-admin-add').classList.add('active');
            document.getElementById('add-status').innerText = "";
        } else if (tabKey === 'admin-manage') {
            document.getElementById('content-admin-manage').classList.add('active');
            document.getElementById('btn-tab-admin-manage').classList.add('active');
            loadManageList();
        } else if (tabKey === 'admin') {
            document.getElementById('content-admin').classList.add('active');
            document.getElementById('btn-tab-admin').classList.add('active');
            loadAdminLogs();
        }
    }

    function renderSidebar() {
        const sidebar = document.getElementById("prob-sidebar");
        sidebar.innerHTML = `<h3 style='margin-top:0; font-size:14px;'>${currentLang === 'vi' ? 'Danh sách bài tập' : 'Problem List'}</h3>`;
        problems.forEach(p => {
            let btn = document.createElement("button");
            btn.className = `btn-prob ${p.id === currentId ? 'active' : ''}`;
            btn.innerHTML = `<span>${p.name}</span>`;
            btn.onclick = () => { currentId = p.id; loadProblemDetail(); renderSidebar(); };
            sidebar.appendChild(btn);
        });
    }

    function loadProblemDetail() {
        const p = problems.find(x => x.id === currentId);
        if (!p) return;
        document.getElementById("d-title").innerHTML = p.name;
        document.getElementById("d-desc").innerHTML = p.desc;
        document.getElementById("d-sample-in").innerText = p.sampleIn;
        document.getElementById("d-sample-out").innerText = p.sampleOut;
        document.getElementById("d-io-section").style.display = "block";
    }

    function goHome() {
        switchMainTab('list');
    }

    // Tải dữ liệu code đã lưu từ bộ nhớ trình duyệt (giữ lại khi thoát trang, lưu riêng từng bài)
    let codeStorage = JSON.parse(localStorage.getItem('codeStorage')) || {};

    function goToIde(probId) {
        if (probId !== undefined) {
            currentId = probId;
        }
        
        const p = problems.find(x => x.id === currentId);
        if (!p) return;

        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.getElementById('content-ide').classList.add('active');
        document.getElementById('ide-prob-title').innerHTML = p.name;
        document.getElementById('summary').innerText = "";
        document.getElementById('test-results-list').innerHTML = "";

        const textarea = document.getElementById('code-textarea');
        
        if (codeStorage[currentId] !== undefined) {
            textarea.value = codeStorage[currentId];
        } else {
            textarea.value = `#include <iostream>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}`;
        }
    }

    // Tự động lưu toàn bộ dữ liệu code vào localStorage ngay khi gõ phím
    document.addEventListener("DOMContentLoaded", () => {
        const textarea = document.getElementById('code-textarea');
        if (textarea) {
            textarea.addEventListener('input', () => {
                codeStorage[currentId] = textarea.value;
                localStorage.setItem('codeStorage', JSON.stringify(codeStorage));
            });
        }
    });

    async function addNewProblem() {
        let name = document.getElementById('new-name').value.trim();
        let desc = document.getElementById('new-desc').value.trim();
        let sampleIn = document.getElementById('new-sample-in').value;
        let sampleOut = document.getElementById('new-sample-out').value;
        let generatorCode = document.getElementById('new-generator').value;
        let statusDiv = document.getElementById('add-status');

        if (!name || !desc) {
            statusDiv.style.color = '#da3633';
            statusDiv.innerText = currentLang === 'vi' ? "❌ Vui lòng nhập đầy đủ tên và mô tả bài tập!" : "❌ Please enter name and description!";
            return;
        }

        statusDiv.style.color = '#d29922';
        statusDiv.innerText = currentLang === 'vi' ? "⏳ Đang xử lý và sinh bộ test cases..." : "⏳ Generating test cases...";

        let res = await fetch('/admin/add-problem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, desc, sampleIn, sampleOut, generatorCode })
        });
        let data = await res.json();

        if (data.status === "success") {
            statusDiv.style.color = '#238636';
            statusDiv.innerText = currentLang === 'vi' ? `✅ Thêm bài thành công! Đã sinh ra ${data.testCount} test cases.` : `✅ Added successfully! Generated ${data.testCount} test cases.`;
            setTimeout(() => switchMainTab('list'), 1500);
        } else {
            statusDiv.style.color = '#da3633';
            statusDiv.innerText = `❌ Lỗi: ${data.message}`;
        }
    }

    async function loadManageList() {
        let res = await fetch('/admin/problems-full');
        let data = await res.json();
        let select = document.getElementById('manage-select-prob');
        select.innerHTML = "";
        data.forEach(p => {
            let opt = document.createElement('option');
            opt.value = p.id;
            opt.text = `#${p.id} - ${p.name.replace(/<[^>]*>?/gm, '')}`;
            select.appendChild(opt);
        });
        if (data.length > 0) {
            select.selectedIndex = 0;
            loadProblemForEdit();
        }
    }

    async function loadProblemForEdit() {
        let id = document.getElementById('manage-select-prob').value;
        if (!id) return;
        let res = await fetch(`/admin/problem/${id}`);
        let p = await res.json();
        
        document.getElementById('edit-id').value = p.id;
        document.getElementById('edit-name').value = p.name;
        document.getElementById('edit-desc').value = p.desc;
        document.getElementById('edit-sample-in').value = p.sampleIn;
        document.getElementById('edit-sample-out').value = p.sampleOut;
        document.getElementById('edit-tests').value = JSON.stringify(p.tests, null, 2);
        document.getElementById('edit-status').innerText = "";
    }

    async function updateProblem() {
        let id = document.getElementById('edit-id').value;
        let name = document.getElementById('edit-name').value;
        let desc = document.getElementById('edit-desc').value;
        let sampleIn = document.getElementById('edit-sample-in').value;
        let sampleOut = document.getElementById('edit-sample-out').value;
        let testsRaw = document.getElementById('edit-tests').value;
        let statusDiv = document.getElementById('edit-status');

        let tests;
        try { tests = JSON.parse(testsRaw); } catch (e) {
            statusDiv.style.color = '#da3633';
            statusDiv.innerText = currentLang === 'vi' ? "❌ Định dạng JSON của Test Cases không hợp lệ!" : "❌ Invalid JSON format for Test Cases!";
            return;
        }

        let res = await fetch(`/admin/update-problem/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, desc, sampleIn, sampleOut, tests })
        });
        let data = await res.json();
        if (data.status === "success") {
            statusDiv.style.color = '#238636';
            statusDiv.innerText = currentLang === 'vi' ? "✅ Cập nhật bài tập thành công!" : "✅ Problem updated successfully!";
            loadManageList();
        } else {
            statusDiv.style.color = '#da3633';
            statusDiv.innerText = "❌ Lỗi: " + data.message;
        }
    }

    async function deleteProblem() {
        let id = document.getElementById('edit-id').value;
        if (!confirm(currentLang === 'vi' ? "Bạn có chắc chắn muốn xóa bài tập này không?" : "Are you sure to delete this problem?")) return;
        let res = await fetch(`/admin/delete-problem/${id}`, { method: 'DELETE' });
        let data = await res.json();
        if (data.status === "success") { alert("Deleted!"); loadManageList(); }
    }

    async function submitCode() {
        const code = document.getElementById('code-textarea').value;
        const summary = document.getElementById("summary");
        const resultsContainer = document.getElementById("test-results-list");

        summary.innerText = currentLang === 'vi' ? "⏳ Đang biên dịch và chấm điểm..." : "⏳ Compiling and grading...";
        resultsContainer.innerHTML = "";

        let res = await fetch('/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ problemId: currentId, code })
        });
        let data = await res.json();

        if (data.verdict === "CE") {
            summary.innerText = currentLang === 'vi' ? "❌ Lỗi Biên dịch (Compilation Error):" : "❌ Compilation Error:";
            resultsContainer.innerHTML = `
                <div class="test-case-card">
                    <div class="test-case-header" style="background:#da3633; color:white;" onclick="toggleTestDetail(this)">
                        <span>Chi tiết lỗi biên dịch</span>
                        <span>▼</span>
                    </div>
                    <div class="test-case-body" style="display:block; color:#ff7b72;"><pre>${data.message}</pre></div>
                </div>`;
            return;
        }

        summary.innerText = currentLang === 'vi' ? `🎯 Kết quả: Vượt qua ${data.passed}/${data.total} test cases. (${data.overall})` : `🎯 Result: Passed ${data.passed}/${data.total} test cases. (${data.overall})`;

        data.results.forEach(t => {
            let card = document.createElement("div");
            card.className = "test-case-card";
            card.innerHTML = `
                <div class="test-case-header" onclick="toggleTestDetail(this)">
                    <span>Test #${t.test}</span>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="badge ${t.status}">${t.status}</span>
                        <span style="font-size: 11px;">▼</span>
                    </div>
                </div>
                <div class="test-case-body">
                    <strong>Input:</strong><pre style="margin:4px 0 10px 0; color:#dcdcaa; white-space: pre-wrap;">${t.input}</pre>
                    <strong>Expected:</strong><pre style="margin:4px 0 10px 0; color:#7ee787; white-space: pre-wrap;">${t.expected}</pre>
                    <strong>Output:</strong><pre style="margin:4px 0 0 0; color:#ff7b72; white-space: pre-wrap;">${t.output}</pre>
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }

    function toggleTestDetail(headerElem) {
        let body = headerElem.nextElementSibling;
        body.style.display = body.style.display === "block" ? "none" : "block";
    }

    async function loadAdminLogs() {
        let res = await fetch('/admin/logs');
        allLogs = await res.json();
        let tbody = document.getElementById("admin-log-body");
        tbody.innerHTML = "";
        if (allLogs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">${currentLang === 'vi' ? 'Chưa có dữ liệu.' : 'No data available.'}</td></tr>`;
            document.getElementById("submission-detail-container").style.display = "none";
            return;
        }
        
        let reversedLogs = [...allLogs].reverse();
        reversedLogs.forEach((log, idx) => {
            let originalIndex = allLogs.length - 1 - idx;
            let tr = document.createElement("tr");
            tr.className = "clickable-row";
            tr.onclick = () => viewSubmissionDetail(originalIndex);
            tr.innerHTML = `<td>#${allLogs.length - idx}</td><td>${log.time}</td><td>${log.problem}</td><td>${log.detail}</td><td><span class="badge ${log.status}">${log.status}</span></td>`;
            tbody.appendChild(tr);
        });
    }

    function viewSubmissionDetail(index) {
        let log = allLogs[index];
        if (!log) return;

        document.getElementById("submission-detail-container").style.display = "block";
        document.getElementById("log-view-code").value = log.code || "";
        
        let container = document.getElementById("log-view-tests");
        container.innerHTML = "";

        if (!log.results || log.results.length === 0) {
            container.innerHTML = `<div style="padding: 10px; font-family: monospace;">Biên dịch thất bại hoặc không có test case chi tiết.</div>`;
            return;
        }

        log.results.forEach(t => {
            let card = document.createElement("div");
            card.className = "test-case-card";
            card.innerHTML = `
                <div class="test-case-header" onclick="toggleTestDetail(this)">
                    <span>Test #${t.test}</span>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="badge ${t.status}">${t.status}</span>
                        <span style="font-size: 11px;">▼</span>
                    </div>
                </div>
                <div class="test-case-body">
                    <strong>Input:</strong><pre style="margin:4px 0 10px 0; color:#dcdcaa; white-space: pre-wrap;">${t.input}</pre>
                    <strong>Expected:</strong><pre style="margin:4px 0 10px 0; color:#7ee787; white-space: pre-wrap;">${t.expected}</pre>
                    <strong>Output:</strong><pre style="margin:4px 0 0 0; color:#ff7b72; white-space: pre-wrap;">${t.output}</pre>
                </div>
            `;
            container.appendChild(card);
        });

        document.getElementById("submission-detail-container").scrollIntoView({ behavior: 'smooth' });
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/problems', methods=['GET'])
def get_problems():
    client_problems = []
    for p in problems_db:
        client_problems.append({
            "id": p["id"],
            "name": p["name"],
            "desc": p["desc"],
            "sampleIn": p["sampleIn"],
            "sampleOut": p["sampleOut"]
        })
    return jsonify(client_problems)

@app.route('/admin/problems-full', methods=['GET'])
def admin_problems_full():
    return jsonify(problems_db)

@app.route('/admin/problem/<int:pid>', methods=['GET'])
def admin_get_problem(pid):
    p = next((x for x in problems_db if x["id"] == pid), None)
    if not p:
        return jsonify({"error": "Not found"}), 404
    return jsonify(p)

@app.route('/admin/update-problem/<int:pid>', methods=['PUT'])
def admin_update_problem(pid):
    data = request.json
    p = next((x for x in problems_db if x["id"] == pid), None)
    if not p:
        return jsonify({"status": "error", "message": "Không tìm thấy bài tập!"}), 404
    
    p["name"] = data.get('name', p["name"])
    p["desc"] = data.get('desc', p["desc"])
    p["sampleIn"] = data.get('sampleIn', p["sampleIn"])
    p["sampleOut"] = data.get('sampleOut', p["sampleOut"])
    p["tests"] = data.get('tests', p["tests"])
    
    return jsonify({"status": "success"})

@app.route('/admin/delete-problem/<int:pid>', methods=['DELETE'])
def admin_delete_problem(pid):
    global problems_db
    problems_db = [x for x in problems_db if x["id"] != pid]
    return jsonify({"status": "success"})

@app.route('/admin/add-problem', methods=['POST'])
def add_problem():
    data = request.json
    name = data.get('name')
    desc = data.get('desc')
    sample_in = data.get('sampleIn')
    sample_out = data.get('sampleOut')
    generator_code = data.get('generatorCode', '')

    tests = []
    try:
        local_env = {}
        exec(generator_code, {}, local_env)
        if 'tests' in local_env and isinstance(local_env['tests'], list):
            tests = local_env['tests']
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    if not tests:
        return jsonify({"status": "error", "message": "Mã không tạo ra test case nào."}), 400

    new_id = max([p["id"] for p in problems_db], default=0) + 1
    problems_db.append({
        "id": new_id,
        "name": name,
        "desc": desc,
        "sampleIn": sample_in,
        "sampleOut": sample_out,
        "tests": tests
    })

    return jsonify({"status": "success", "testCount": len(tests)})

@app.route('/admin/logs', methods=['GET'])
def admin_logs():
    return jsonify(global_submissions)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    problem_id = int(data.get('problemId'))
    code = data.get('code')

    target_problem = next((p for p in problems_db if p["id"] == problem_id), None)
    if not target_problem:
        return jsonify({"verdict": "CE", "message": "Không tìm thấy bài tập!"})

    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "solution.cpp")
        exe_path = os.path.join(tmpdir, "solution")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(code)

        compile_res = subprocess.run(["g++", src_path, "-o", exe_path], capture_output=True, text=True)
        if compile_res.returncode != 0:
            global_submissions.append({
                "time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
                "problem": target_problem["name"],
                "detail": "Biên dịch thất bại",
                "status": "CE",
                "code": code,
                "results": []
            })
            return jsonify({"verdict": "CE", "message": compile_res.stderr})

        tests = target_problem["tests"]
        results = []
        passed_count = 0
        overall_status = "AC"

        for idx, test in enumerate(tests, 1):
            status = "AC"
            output = ""
            try:
                run_res = subprocess.run([exe_path], input=test["input"], capture_output=True, text=True, timeout=1.5)
                if run_res.returncode != 0:
                    status = "RTE"
                    output = run_res.stderr or f"Exit code {run_res.returncode}"
                else:
                    output = run_res.stdout
                    if output.strip() != test["expected"].strip():
                        status = "WA"
            except subprocess.TimeoutExpired:
                status = "TLE"
                output = "Time Limit Exceeded"
            except Exception as e:
                status = "RTE"
                output = str(e)

            if status == "AC":
                passed_count += 1
            else:
                overall_status = status

            results.append({
                "test": idx,
                "status": status,
                "input": test["input"],
                "expected": test["expected"],
                "output": output
            })

        global_submissions.append({
            "time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "problem": target_problem["name"],
            "detail": f"Vượt qua {passed_count}/{len(tests)} test cases",
            "status": overall_status,
            "code": code,
            "results": results
        })

        return jsonify({
            "verdict": "OK",
            "passed": passed_count,
            "total": len(tests),
            "overall": overall_status,
            "results": results
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
