"""
共用 helper（給 generate_showcase / generate_event_map / generate_event_map_print 使用）
"""

import copy


def mask_name(name):
    """姓名屏蔽：保留首尾，中間以 O 取代。

    範例：
      ''       → ''
      '王'      → '王'
      '王明'    → '王O'
      '王小明'  → '王O明'
      '歐陽小明' → '歐OO明'

    註：不假設「姓」幾個字（不偵測複姓），統一首尾保留、中間全 O。
    """
    s = str(name or '').strip()
    n = len(s)
    if n <= 1:
        return s
    if n == 2:
        return s[0] + 'O'
    return s[0] + 'O' * (n - 2) + s[-1]


def with_masked_names(class_data):
    """回傳一份深拷貝，所有 student.name 與 student.id 中的姓名都已被屏蔽。

    id 格式為 「班級_座號_姓名」，會用屏蔽後的姓名重組。
    呼叫端拿這份副本去渲染與 inline JSON，避免明碼姓名外流。
    """
    data = copy.deepcopy(class_data)
    for st in data.get('students', []):
        original_name = st.get('name', '')
        masked = mask_name(original_name)
        st['name'] = masked

        old_id = st.get('id', '')
        if old_id and original_name and original_name in old_id:
            st['id'] = old_id.replace(original_name, masked)

        old_src = st.get('source_file', '')
        if old_src and original_name and original_name in old_src:
            st['source_file'] = old_src.replace(original_name, masked)

        if original_name:
            for key in ('peer_review', 'legacy_supplement', 'ai_process', 'sources'):
                if key in st:
                    st[key] = _replace_name_deep(st[key], original_name, masked)
    return data


def _replace_name_deep(value, original, masked):
    if isinstance(value, str):
        return value.replace(original, masked)
    if isinstance(value, list):
        return [_replace_name_deep(v, original, masked) for v in value]
    if isinstance(value, dict):
        return {k: _replace_name_deep(v, original, masked) for k, v in value.items()}
    return value
