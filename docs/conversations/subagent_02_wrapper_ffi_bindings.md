# Conversation Archive: Subagent 02: wrapper.py FFI Bindings & ctypes Interface

- **Session ID**: `8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad`
- **Role**: FFI / C-Types Specialist
- **Type**: Subagent
- **Total Turns**: 1
- **Timeline**: 2026-08-11T02:52:03Z to 2026-08-11T02:52:03Z

---

## Turn 1 (Step 0)
*Timestamp: 2026-08-11T02:52:03Z*

### 👤 User
Update p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\wrapper.py to bind cortiq_imagine in CMFWrapper and implement generate_image method that outputs PyTorch IMAGE tensor [1, H, W, 3].

### ⚙️ Actions & Tool Execution
<details>
<summary>Executed Tools and Actions (13 actions)</summary>

- **`view_file`**: view_file — Viewed ``
- **`find_by_name`**: find_by_name
- **`grep_search`**: grep_search
- **`grep_search`**: grep_search
- **`view_file`**: view_file — Viewed ``
- **`run_command`**: run_command
- **`manage_task`**: manage_task
- **`view_file`**: view_file — Viewed ``
- **`multi_replace_file_content`**: multi_replace_file_content — File: `` - 
- **`run_command`**: run_command
- **`manage_task`**: manage_task
- **`view_file`**: view_file — Viewed ``
- **`send_message`**: send_message

</details>

### 🤖 Assistant
Created At: 2026-08-10T19:52:06-07:00
Completed At: 2026-08-10T19:52:06-07:00
File Path: `file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/custom_nodes/Comfy-CMF/wrapper.py`
Total Lines: 251
Total Bytes: 10428
Showing lines 1 to 251
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import ctypes
2: import os
3: import sys
4: import json
5: from pathlib import Path
6: 
7: class CMFWrapper:
8:     """
9:     Python ctypes wrapper for the CMF (Cortiq Model Format) Rust FFI library (cortiq-ffi).
10:     Manages loading the native dynamic library, defining C ABI signatures, GPU toggles, and error inspection.
11:     """
12:     
13:     def __init__(self, lib_path=None):
14:         if lib_path is None:
15:             lib_path = self._find_library()
16:             
17:         if not os.path.exists(lib_path):
18:             raise FileNotFoundError(
19:                 f"[ComfyUI-CMF] Shared library not found at: '{lib_path}'. "
20:                 "Please place cortiq_ffi.dll (Windows), libcortiq_ffi.so (Linux), or "
21:                 "libcortiq_ffi.dylib (macOS) in the 'bin/' directory, or build using "
22:                 "'cargo build -p cortiq-ffi --release'."
23:             )
24:             
25:         try:
26:             self.lib = ctypes.CDLL(lib_path)
27:         except Exception as e:
28:             raise RuntimeError(f"[ComfyUI-CMF] Failed to load dynamic library '{lib_path}': {e}")
29:             
30:         self._bind_signatures()
31: 
32:     def _find_library(self) -> str:
33:         """Dynamically detect host OS and locate cortiq_ffi dynamic library."""
34:         base_dir = Path(__file__).parent / "bin"
35:         
36:         if sys.platform == "win32":
37:             lib_name = "cortiq_ffi.dll"
38:         elif sys.platform == "darwin":
39:             lib_name = "libcortiq_ffi.dylib"
40:         else:
41:             lib_name = "libcortiq_ffi.so"
42:             
43:         target = base_dir / lib_name
44:         if target.exists():
45:             return str(target)
46:             
47:         alt_target = Path(__file__).parent / lib_name
48:         if alt_target.exists():
49:             return str(alt_target)
50:             
51:         return str(target)
52: 
53:     def _bind_signatures(self):
54:         """Bind C ABI function signatures matching cortiq.h."""
55:         # void *cortiq_load(const char *path);
56:         self.lib.cortiq_load.restype = ctypes.c_void_p
57:         self.lib.cortiq_load.argtypes = [ctypes.c_char_p]
58:         
59:         # void cortiq_set_gpu(bool enable);
60:         if hasattr(self.lib, "cortiq_set_gpu"):
61:             self.lib.cortiq_set_gpu.restype = None
62:             self.lib.cortiq_set_gpu.argtypes = [ctypes.c_bool]
63:             
64:         # void cortiq_set_threads(int32_t n);
65:         if hasattr(self.lib, "cortiq_set_threads"):
66:             self.lib.cortiq_set_threads.restype = None
67:             self.lib.cortiq_set_threads.argtypes = [ctypes.c_int32]
68:             
69:         # int32_t cortiq_set_options(void *handle, const char *json_options);
70:         self.lib.cortiq_set_options.restype = ctypes.c_int32
71:         self.lib.cortiq_set_options.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
72:         
73:         # typedef bool (*cortiq_token_cb)(const char *token, void *user);
74:         self.CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_char_p, ctypes.c_void_p)
75:         
76:         # int32_t cortiq_chat(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);
77:         self.lib.cortiq_chat.restype = ctypes.c_int32
78:         self.lib.cortiq_chat.argtypes = [
79:             ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
80:             self.CALLBACK_TYPE, ctypes.c_void_p
81:         ]
82: 
83:         # int32_t cortiq_chat_messages(void *handle, const char *json_messages, uint32_t max_tokens, cortiq_token_cb cb, void *user);
84:         if hasattr(self.lib, "cortiq_chat_messages"):
85:             self.lib.cortiq_chat_messages.restype = ctypes.c_int32
86:             self.lib.cortiq_chat_messages.argtypes = [
87:                 ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
88:                 self.CALLBACK_TYPE, ctypes.c_void_p
89:             ]
90:         
91:         # void cortiq_cancel(void *handle);
92:         if hasattr(self.lib, "cortiq_cancel"):
93:             self.lib.cortiq_cancel.restype = None
94:             self.lib.cortiq_cancel.argtypes = [ctypes.c_void_p]
95:             
96:         # const char *cortiq_last_error(void);
97:         if hasattr(self.lib, "cortiq_last_error"):
98:             self.lib.cortiq_last_error.restype = ctypes.c_char_p
99:             self.lib.cortiq_last_error.argtypes = []
100: 
101:         # const char *cortiq_execution_info(void);
102:         if hasattr(self.lib, "cortiq_execution_info"):
103:             self.lib.cortiq_execution_info.restype = ctypes.c_char_p
104:             self.lib.cortiq_execution_info.argtypes = []
105: 
106:         # void cortiq_free(void *handle);
107:         self.lib.cortiq_free.restype = None
108:         self.lib.cortiq_free.argtypes = [ctypes.c_void_p]
109: 
110:     def set_gpu(self, enable: bool = True):
111:         """Enable or disable discrete GPU graph acceleration (Vulkan / Metal). Must be called before load."""
112:         if hasattr(self.lib, "cortiq_set_gpu"):
113:             self.lib.cortiq_set_gpu(enable)
114: 
115:     def set_threads(self, num_threads: int = 0):
116:         """Set execution thread pool count (0 = automatic based on physical CPU cores)."""
117:         if hasattr(self.lib, "cortiq_set_threads"):
118:             self.lib.cortiq_set_threads(num_threads)
119: 
120:     def get_last_error(self) -> str:
121:         """Extract thread-local diagnostic error string from C runtime."""
122:         if hasattr(self.lib, "cortiq_last_error"):
123:             err_ptr = self.lib.cortiq_last_error()
124:             if err_ptr:
125:                 return ctypes.string_at(err_ptr).decode("utf-8", errors="replace")
126:         return "Unknown CMF FFI error"
127: 
128:     def get_execution_info(self) -> str:
129:         """Query execution environment info JSON."""
130:         if hasattr(self.lib, "cortiq_execution_info"):
131:             info_ptr = self.lib.cortiq_execution_info()
132:             if info_ptr:
133:                 return ctypes.string_at(info_ptr).decode("utf-8", errors="replace")
134:         return "{}"
135: 
136:     def load_model(self, model_path: str, enable_gpu: bool = True, num_threads: int = 0):
137:         """Memory-map and open a .cmf model file, returning a CMFModelHandle."""
138:         if not os.path.exists(model_path):
139:             raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
140:             
141:         self.set_gpu(enable_gpu)
142:         self.set_threads(num_threads)
143:         
144:         handle = self.lib.cortiq_load(model_path.encode("utf-8"))
145:         if not handle:
146:             err = self.get_last_error()
147:             raise RuntimeError(f"[ComfyUI-CMF] Failed to load model '{model_path}': {err}")
148:             
149:         return CMFModelHandle(self, handle, model_path)
150: 
151: 
152: class CMFModelHandle:
153:     """
154:     RAII wrapper around CMF opaque void* model handles.
155:     Ensures memory-mapped files and C memory structures are freed via cortiq_free.
156:     """
157:     
158:     def __init__(self, wrapper: CMFWrapper, handle: int, path: str):
159:         self.wrapper = wrapper
160:         self.handle = handle
161:         self.path = path
162:         self._closed = False
163: 
164:     def set_options(self, options_dict: dict):
165:         """Serialize sampler options to JSON and pass to Rust runtime."""
166:         if self._closed or not self.handle:
167:             raise RuntimeError("[ComfyUI-CMF] Attempted to set options on closed model handle.")
168:             
169:         opt_json = json.dumps(options_dict).encode("utf-8")
170:         res = self.wrapper.lib.cortiq_set_options(self.handle, opt_json)
171:         if res != 0:
172:             err = self.wrapper.get_last_error()
173:             raise RuntimeError(f"[ComfyUI-CMF] Failed to set options: {err}")
174: 
175:     def generate(self, prompt: str, max_tokens: int, interrupt_check_fn=None) -> str:
176:         """
177:         Execute single-turn streaming prompt generation.
178:         Checks interrupt_check_fn periodically and invokes cortiq_cancel if requested.
179:         """
180:         if self._closed or not self.handle:
181:             raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
182:             
183:         output_tokens = []
184:         
185:         def py_callback(token_ptr, user_data):
186:             if interrupt_check_fn and interrupt_check_fn():
187:                 if hasattr(self.wrapper.lib, "cortiq_cancel"):
188:                     self.wrapper.lib.cortiq_cancel(self.handle)
189:                 return False
190:                 
191:             if token_ptr:
192:                 token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
193:                 output_tokens.append(token_str)
194:             return True
195: 
196:         c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
197:         
198:         res = self.wrapper.lib.cortiq_chat(
199:             self.handle, prompt.encode("utf-8"), max_tokens, c_callback, None
200:         )
201:         
202:         if res < 0:
203:             err = self.wrapper.get_last_error()
204:             raise RuntimeError(f"[ComfyUI-CMF] Text generation failed: {err}")
205:             
206:         return "".join(output_tokens)
207: 
208:     def generate_messages(self, messages_list: list, max_tokens: int, interrupt_check_fn=None) -> str:
209:         """Execute multi-turn chat template generation using cortiq_chat_messages."""
210:         if self._closed or not self.handle:
211:             raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
212:             
213:         if not hasattr(self.wrapper.lib, "cortiq_chat_messages"):
214:             raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_chat_messages support.")
215:             
216:         output_tokens = []
217:         
218:         def py_callback(token_ptr, user_data):
219:             if interrupt_check_fn and interrupt_check_fn():
220:                 if hasattr(self.wrapper.lib, "cortiq_cancel"):
221:                     self.wrapper.lib.cortiq_cancel(self.handle)
222:                 return False
223:                 
224:             if token_ptr:
225:                 token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
226:                 output_tokens.append(token_str)
227:             return True
228: 
229:         c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
230:         msgs_json = json.dumps(messages_list).encode("utf-8")
231:         
232:         res = self.wrapper.lib.cortiq_chat_messages(
233:             self.handle, msgs_json, max_tokens, c_callback, None
234:         )
235:         
236:         if res < 0:
237:             err = self.wrapper.get_last_error()
238:             raise RuntimeError(f"[ComfyUI-CMF] Chat messages generation failed: {err}")
239:             
240:         return "".join(output_tokens)
241: 
242:     def close(self):
243:         """Explicitly release Rust model handle and unmap memory."""
244:         if not self._closed and self.handle:
245:             self.wrapper.lib.cortiq_free(self.handle)
246:             self.handle = None
247:             self._closed = True
248: 
249:     def __del__(self):
250:         self.close()
251: 
The above content shows the entire, complete file contents of the requested file.

{{ CHECKPOINT 0 }}
 **The earlier parts of this conversation have been truncated due to its long length. The following content summarizes the truncated context so that you may continue your work. **


# USER Objective:
Update CMFWrapper Image Generation

# User Requests
The following were user requests from the truncated conversation in chronological order:
1. Update p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\wrapper.py to bind cortiq_imagine in CMFWrapper and implement generate_image method that outputs PyTorch IMAGE tensor [1, H, W, 3].

# Conversation Logs

Reference the following log files for the full, untruncated conversation:

- C:\Users\blibd\.gemini\antigravity\brain\8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad\.system_generated\logs\transcript.jsonl

**IMPORTANT: this summary is just for your reference. You may respond to my previous and future messages, but DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE. JUST READ IT BUT DO NOT MENTION IT, RESPOND TO IT, OR TAKE ACTION BECAUSE OF IT.**

Created At: 2026-08-10T19:52:08-07:00
Completed At: 2026-08-10T19:52:08-07:00
Found 20 results
DECISION_REGISTER.md
README.md
__init__.py
__pycache__
__pycache__/__init__.cpython-312.pyc
__pycache__/__init__.cpython-313.pyc
__pycache__/nodes.cpython-312.pyc
__pycache__/nodes.cpython-313.pyc
__pycache__/wrapper.cpython-312.pyc
__pycache__/wrapper.cpython-313.pyc
bin
bin/cortiq_ffi.dll
bin/cortiq_ffi.dll.lib
bin/cortiq_ffi.lib
cmf_.txt
docs
docs/ARCHITECTURE.md
docs/NEXT_AGENT_HANDOFF.md
nodes.py
wrapper.py

Created At: 2026-08-10T19:52:12-07:00
Completed At: 2026-08-10T19:52:12-07:00
{"File":"p:\\Downloaded\\ComfyUI_windows_portable\\ComfyUI\\custom_nodes\\Comfy-CMF\\bin\\cortiq_ffi.dll.lib"}
{"File":"p:\\Downloaded\\ComfyUI_windows_portable\\ComfyUI\\custom_nodes\\Comfy-CMF\\bin\\cortiq_ffi.lib"}

Created At: 2026-08-10T19:52:15-07:00
Completed At: 2026-08-10T19:52:16-07:00
No results found

Created At: 2026-08-10T19:52:18-07:00
Completed At: 2026-08-10T19:52:19-07:00
File Path: `file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/custom_nodes/Comfy-CMF/nodes.py`
Total Lines: 182
Total Bytes: 6278
Showing lines 1 to 182
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import os
2: import sys
3: import folder_paths
4: import comfy.model_management
5: from .wrapper import CMFWrapper, CMFModelHandle
6: 
7: # Global wrapper singleton
8: _wrapper_instance = None
9: 
10: def get_cmf_wrapper():
11:     """Lazy initialize global CMFWrapper singleton."""
12:     global _wrapper_instance
13:     if _wrapper_instance is None:
14:         _wrapper_instance = CMFWrapper()
15:     return _wrapper_instance
16: 
17: 
18: class CMFModelLoader:
19:     """
20:     ComfyUI Node to select and load Cortiq Model Format (.cmf) files.
21:     Discovers files in ComfyUI/models/cmf/ directory.
22:     Exposes GPU acceleration and thread pool controls.
23:     """
24:     
25:     @classmethod
26:     def INPUT_TYPES(cls):
27:         # Retrieve list of available .cmf models from folder_paths
28:         cmf_models = folder_paths.get_filename_list("cmf")
29:         if not cmf_models:
30:             # Fallback check
31:             cmf_dir = os.path.join(folder_paths.models_dir, "cmf")
32:             if os.path.exists(cmf_dir):
33:                 cmf_models = [f for f in os.listdir(cmf_dir) if f.endswith(".cmf")]
34:             if not cmf_models:
35:                 cmf_models = ["none_found"]
36:                 
37:         return {
38:             "required": {
39:                 "model_name": (cmf_models,),
40:                 "enable_gpu": ("BOOLEAN", {"default": True}),
41:                 "threads": ("INT", {"default": 0, "min": 0, "max": 64, "step": 1}),
42:             }
43:         }
44: 
45:     RETURN_TYPES = ("CMF_MODEL",)
46:     RETURN_NAMES = ("model",)
47:     FUNCTION = "load"
48:     CATEGORY = "Cortiq/CMF"
49: 
50:     def load(self, model_name, enable_gpu=True, threads=0):
51:         if model_name == "none_found":
52:             raise RuntimeError(
53:                 "[ComfyUI-CMF] No .cmf files found in 'ComfyUI/models/cmf/'. "
54:                 "Please place your CMF quantized model files in that directory."
55:             )
56:             
57:         wrapper = get_cmf_wrapper()
58:         full_path = folder_paths.get_full_path("cmf", model_name)
59:         if not full_path:
60:             full_path = os.path.join(folder_paths.models_dir, "cmf", model_name)
61:             
62:         handle = wrapper.load_model(full_path, enable_gpu=enable_gpu, num_threads=threads)
63:         return (handle,)
64: 
65: 
66: class CMFSamplerOptions:
67:     """
68:     ComfyUI Node to configure text generation sampling parameters
69:     (temperature, top_p, top_k, repetition penalty, greedy, seed).
70:     """
71:     
72:     @classmethod
73:     def INPUT_TYPES(cls):
74:         return {
75:             "required": {
76:                 "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01}),
77:                 "top_p": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.01}),
78:                 "top_k": ("INT", {"default": 40, "min": 0, "max": 200, "step": 1}),
79:                 "repetition_penalty": ("FLOAT", {"default": 1.1, "min": 1.0, "max": 2.0, "step": 0.01}),
80:                 "greedy": ("BOOLEAN", {"default": False}),
81:                 "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
82:             }
83:         }
84: 
85:     RETURN_TYPES = ("CMF_OPTIONS",)
86:     RETURN_NAMES = ("options",)
87:     FUNCTION = "configure"
88:     CATEGORY = "Cortiq/CMF"
89: 
90:     def configure(self, temperature, top_p, top_k, repetition_penalty, greedy, seed):
91:         options = {
92:             "temperature": temperature,
93:             "top_p": top_p,
94:             "top_k": top_k,
95:             "repetition_penalty": repetition_penalty,
96:             "greedy": greedy,
97:             "seed": seed,
98:         }
99:         return (options,)
100: 
101: 
102: class CMFTextGenerate:
103:     """
104:     ComfyUI Node for single-turn prompt text generation.
105:     Supports periodic ComfyUI processing interruption checks.
106:     """
107:     
108:     @classmethod
109:     def INPUT_TYPES(cls):
110:         return {
111:             "required": {
112:                 "model": ("CMF_MODEL",),
113:                 "prompt": ("STRING", {"multiline": True, "default": "Write a short poem about artificial intelligence."}),
114:                 "max_tokens": ("INT", {"default": 256, "min": 1, "max": 8192, "step": 1}),
115:             },
116:             "optional": {
117:                 "options": ("CMF_OPTIONS",),
118:             }
119:         }
120: 
121:     RETURN_TYPES = ("STRING",)
122:     RETURN_NAMES = ("text",)
123:     FUNCTION = "generate"
124:     CATEGORY = "Cortiq/CMF"
125: 
126:     def generate(self, model: CMFModelHandle, prompt: str, max_tokens: int, options: dict = None):
127:         if not isinstance(model, CMFModelHandle):
128:             raise TypeError(f"[ComfyUI-CMF] Invalid model type received: {type(model)}")
129:             
130:         if options:
131:             model.set_options(options)
132: 
133:         def interrupt_check():
134:             return comfy.model_management.processing_interrupted()
135: 
136:         result = model.generate(prompt, max_tokens, interrupt_check_fn=interrupt_check)
137:         return (result,)
138: 
139: 
140: class CMFChatGenerate:
141:     """
142:     ComfyUI Node for multi-turn structured chat generation (System Prompt + User Prompt).
143:     Uses cortiq_chat_messages FFI call.
144:     """
145:     
146:     @classmethod
147:     def INPUT_TYPES(cls):
148:         return {
149:             "required": {
150:                 "model": ("CMF_MODEL",),
151:                 "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful, creative AI assistant."}),
152:                 "user_prompt": ("STRING", {"multiline": True, "default": "How does memory mapping improve model loading speed?"}),
153:                 "max_tokens": ("INT", {"default": 256, "min": 1, "max": 8192, "step": 1}),
154:             },
155:             "optional": {
156:                 "options": ("CMF_OPTIONS",),
157:             }
158:         }
159: 
160:     RETURN_TYPES = ("STRING",)
161:     RETURN_NAMES = ("response",)
162:     FUNCTION = "generate_chat"
163:     CATEGORY = "Cortiq/CMF"
164: 
165:     def generate_chat(self, model: CMFModelHandle, system_prompt: str, user_prompt: str, max_tokens: int, options: dict = None):
166:         if not isinstance(model, CMFModelHandle):
167:             raise TypeError(f"[ComfyUI-CMF] Invalid model type received: {type(model)}")
168:             
169:         if options:
170:             model.set_options(options)
171: 
172:         messages = [
173:             {"role": "system", "content": system_prompt},
174:             {"role": "user", "content": user_prompt}
175:         ]
176: 
177:         def interrupt_check():
178:             return comfy.model_management.processing_interrupted()
179: 
180:         result = model.generate_messages(messages, max_tokens, interrupt_check_fn=interrupt_check)
181:         return (result,)
182: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-10T19:52:25-07:00
Tool is running as a background task with task id: 8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-13
Task Description: python -c "import numpy as np; import torch; print(np.__version__, torch.__version__)"
Task logs are available at: file:///C:/Users/blibd/.gemini/antigravity/brain/8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/.system_generated/tasks/task-13.log

Created At: 2026-08-10T19:52:33-07:00
Completed At: 2026-08-10T19:52:33-07:00
Task: 8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-13
Status: RUNNING
Log: C:\Users\blibd\.gemini\antigravity\brain\8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad\.system_generated\tasks\task-13.log
Last progress: never


REMINDER: Do not call this tool again to poll or wait for updates. You will be automatically notified when the task completes or a message arrives. If you need a bounded wait, use the `schedule` tool -- it waits silently in the background and suppresses its notification if you are woken by another event.

Created At: 2026-08-10T19:52:36-07:00
Completed At: 2026-08-10T19:52:36-07:00
File Path: `file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/custom_nodes/Comfy-CMF/wrapper.py`
Total Lines: 251
Total Bytes: 10428
Showing lines 1 to 150
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import ctypes
2: import os
3: import sys
4: import json
5: from pathlib import Path
6: 
7: class CMFWrapper:
8:     """
9:     Python ctypes wrapper for the CMF (Cortiq Model Format) Rust FFI library (cortiq-ffi).
10:     Manages loading the native dynamic library, defining C ABI signatures, GPU toggles, and error inspection.
11:     """
12:     
13:     def __init__(self, lib_path=None):
14:         if lib_path is None:
15:             lib_path = self._find_library()
16:             
17:         if not os.path.exists(lib_path):
18:             raise FileNotFoundError(
19:                 f"[ComfyUI-CMF] Shared library not found at: '{lib_path}'. "
20:                 "Please place cortiq_ffi.dll (Windows), libcortiq_ffi.so (Linux), or "
21:                 "libcortiq_ffi.dylib (macOS) in the 'bin/' directory, or build using "
22:                 "'cargo build -p cortiq-ffi --release'."
23:             )
24:             
25:         try:
26:             self.lib = ctypes.CDLL(lib_path)
27:         except Exception as e:
28:             raise RuntimeError(f"[ComfyUI-CMF] Failed to load dynamic library '{lib_path}': {e}")
29:             
30:         self._bind_signatures()
31: 
32:     def _find_library(self) -> str:
33:         """Dynamically detect host OS and locate cortiq_ffi dynamic library."""
34:         base_dir = Path(__file__).parent / "bin"
35:         
36:         if sys.platform == "win32":
37:             lib_name = "cortiq_ffi.dll"
38:         elif sys.platform == "darwin":
39:             lib_name = "libcortiq_ffi.dylib"
40:         else:
41:             lib_name = "libcortiq_ffi.so"
42:             
43:         target = base_dir / lib_name
44:         if target.exists():
45:             return str(target)
46:             
47:         alt_target = Path(__file__).parent / lib_name
48:         if alt_target.exists():
49:             return str(alt_target)
50:             
51:         return str(target)
52: 
53:     def _bind_signatures(self):
54:         """Bind C ABI function signatures matching cortiq.h."""
55:         # void *cortiq_load(const char *path);
56:         self.lib.cortiq_load.restype = ctypes.c_void_p
57:         self.lib.cortiq_load.argtypes = [ctypes.c_char_p]
58:         
59:         # void cortiq_set_gpu(bool enable);
60:         if hasattr(self.lib, "cortiq_set_gpu"):
61:             self.lib.cortiq_set_gpu.restype = None
62:             self.lib.cortiq_set_gpu.argtypes = [ctypes.c_bool]
63:             
64:         # void cortiq_set_threads(int32_t n);
65:         if hasattr(self.lib, "cortiq_set_threads"):
66:             self.lib.cortiq_set_threads.restype = None
67:             self.lib.cortiq_set_threads.argtypes = [ctypes.c_int32]
68:             
69:         # int32_t cortiq_set_options(void *handle, const char *json_options);
70:         self.lib.cortiq_set_options.restype = ctypes.c_int32
71:         self.lib.cortiq_set_options.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
72:         
73:         # typedef bool (*cortiq_token_cb)(const char *token, void *user);
74:         self.CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_char_p, ctypes.c_void_p)
75:         
76:         # int32_t cortiq_chat(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);
77:         self.lib.cortiq_chat.restype = ctypes.c_int32
78:         self.lib.cortiq_chat.argtypes = [
79:             ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
80:             self.CALLBACK_TYPE, ctypes.c_void_p
81:         ]
82: 
83:         # int32_t cortiq_chat_messages(void *handle, const char *json_messages, uint32_t max_tokens, cortiq_token_cb cb, void *user);
84:         if hasattr(self.lib, "cortiq_chat_messages"):
85:             self.lib.cortiq_chat_messages.restype = ctypes.c_int32
86:             self.lib.cortiq_chat_messages.argtypes = [
87:                 ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
88:                 self.CALLBACK_TYPE, ctypes.c_void_p
89:             ]
90:         
91:         # void cortiq_cancel(void *handle);
92:         if hasattr(self.lib, "cortiq_cancel"):
93:             self.lib.cortiq_cancel.restype = None
94:             self.lib.cortiq_cancel.argtypes = [ctypes.c_void_p]
95:             
96:         # const char *cortiq_last_error(void);
97:         if hasattr(self.lib, "cortiq_last_error"):
98:             self.lib.cortiq_last_error.restype = ctypes.c_char_p
99:             self.lib.cortiq_last_error.argtypes = []
100: 
101:         # const char *cortiq_execution_info(void);
102:         if hasattr(self.lib, "cortiq_execution_info"):
103:             self.lib.cortiq_execution_info.restype = ctypes.c_char_p
104:             self.lib.cortiq_execution_info.argtypes = []
105: 
106:         # void cortiq_free(void *handle);
107:         self.lib.cortiq_free.restype = None
108:         self.lib.cortiq_free.argtypes = [ctypes.c_void_p]
109: 
110:     def set_gpu(self, enable: bool = True):
111:         """Enable or disable discrete GPU graph acceleration (Vulkan / Metal). Must be called before load."""
112:         if hasattr(self.lib, "cortiq_set_gpu"):
113:             self.lib.cortiq_set_gpu(enable)
114: 
115:     def set_threads(self, num_threads: int = 0):
116:         """Set execution thread pool count (0 = automatic based on physical CPU cores)."""
117:         if hasattr(self.lib, "cortiq_set_threads"):
118:             self.lib.cortiq_set_threads(num_threads)
119: 
120:     def get_last_error(self) -> str:
121:         """Extract thread-local diagnostic error string from C runtime."""
122:         if hasattr(self.lib, "cortiq_last_error"):
123:             err_ptr = self.lib.cortiq_last_error()
124:             if err_ptr:
125:                 return ctypes.string_at(err_ptr).decode("utf-8", errors="replace")
126:         return "Unknown CMF FFI error"
127: 
128:     def get_execution_info(self) -> str:
129:         """Query execution environment info JSON."""
130:         if hasattr(self.lib, "cortiq_execution_info"):
131:             info_ptr = self.lib.cortiq_execution_info()
132:             if info_ptr:
133:                 return ctypes.string_at(info_ptr).decode("utf-8", errors="replace")
134:         return "{}"
135: 
136:     def load_model(self, model_path: str, enable_gpu: bool = True, num_threads: int = 0):
137:         """Memory-map and open a .cmf model file, returning a CMFModelHandle."""
138:         if not os.path.exists(model_path):
139:             raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
140:             
141:         self.set_gpu(enable_gpu)
142:         self.set_threads(num_threads)
143:         
144:         handle = self.lib.cortiq_load(model_path.encode("utf-8"))
145:         if not handle:
146:             err = self.get_last_error()
147:             raise RuntimeError(f"[ComfyUI-CMF] Failed to load model '{model_path}': {err}")
148:             
149:         return CMFModelHandle(self, handle, model_path)
150: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-10T19:52:44-07:00
Completed At: 2026-08-10T19:52:44-07:00
The following changes were made by the multi_replace_file_content tool to: p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\wrapper.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -3,6 +3,9 @@
 import sys
 import json
 from pathlib import Path
+import numpy as np
+import torch
+
 
 class CMFWrapper:
     """
@@ -87,6 +87,33 @@
                 self.CALLBACK_TYPE, ctypes.c_void_p
             ]
         
+        # typedef bool (*cortiq_progress_cb)(uint32_t step, uint32_t total_steps, void *user);
+        self.PROGRESS_CALLBACK_TYPE = ctypes.CFUNCTYPE(
+            ctypes.c_bool, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p
+        )
+
+        # int32_t cortiq_imagine(
+        #     const char *model_path, const char *prompt,
+        #     uint32_t width, uint32_t height, uint32_t steps,
+        #     float guidance, uint64_t seed, uint8_t *out_rgb,
+        #     cortiq_progress_cb progress, void *user
+        # );
+        if hasattr(self.lib, "cortiq_imagine"):
+            self.lib.cortiq_imagine.restype = ctypes.c_int32
+            self.lib.cortiq_imagine.argtypes = [
+                ctypes.c_char_p,
+                ctypes.c_char_p,
+                ctypes.c_uint32,
+                ctypes.c_uint32,
+                ctypes.c_uint32,
+                ctypes.c_float,
+                ctypes.c_uint64,
+                ctypes.POINTER(ctypes.c_uint8),
+                self.PROGRESS_CALLBACK_TYPE,
+                ctypes.c_void_p,
+            ]
+
+        
         # void cortiq_cancel(void *handle);
         if hasattr(self.lib, "cortiq_cancel"):
             self.lib.cortiq_cancel.restype = None
@@ -146,6 +146,63 @@
             
         return CMFModelHandle(self, handle, model_path)
 
+    def generate_image(
+        self,
+        model_path: str,
+        prompt: str,
+        width: int,
+        height: int,
+        steps: int,
+        guidance: float,
+        seed: int,
+        enable_gpu: bool = True,
+        num_threads: int = 0,
+        interrupt_check_fn=None,
+    ) -> torch.Tensor:
+        """
+        Generate an image using cortiq_imagine Rust FFI binding.
+        Allocates uint8 RGB numpy array, populates via C-FFI, and returns float32 PyTorch tensor [1, H, W, 3] normalized in [0.0, 1.0].
+        """
+        if not os.path.exists(model_path):
+            raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
+
+        if not hasattr(self.lib, "cortiq_imagine"):
+            raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_imagine support.")
+
+        self.set_gpu(enable_gpu)
+        self.set_threads(num_threads)
+
+        rgb_np = np.zeros((height, width, 3), dtype=np.uint8)
+        out_ptr = rgb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
+
+        def py_progress_cb(step, total_steps, user_data):
+            if interrupt_check_fn and interrupt_check_fn():
+                return False
+            return True
+
+        c_progress_cb = self.PROGRESS_CALLBACK_TYPE(py_progress_cb)
+
+        res = self.lib.cortiq_imagine(
+            model_path.encode("utf-8"),
+            prompt.encode("utf-8"),
+            int(width),
+            int(height),
+            int(steps),
+            float(guidance),
+            int(seed),
+            out_ptr,
+            c_progress_cb,
+            None,
+        )
+
+        if res < 0:
+            err = self.get_last_error()
+            raise RuntimeError(f"[ComfyUI-CMF] Image generation failed: {err}")
+
+        image_tensor = torch.from_numpy(rgb_np).to(torch.float32) / 255.0
+        return image_tensor.unsqueeze(0)
+
+
 
 class CMFModelHandle:
     """
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

The following is a <SYSTEM_MESSAGE> not actually sent by the user. It is provided by the system as important information to pay attention to.

<SYSTEM_MESSAGE>
[Message] timestamp=2026-08-11T02:52:41Z sender=8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-13 priority=MESSAGE_PRIORITY_HIGH content=Task id "8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-13" finished with result:

				The command exited with code 0.
				Output:
				Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.
2.4.4 2.5.1+cu121


Log: file:///C:/Users/blibd/.gemini/antigravity/brain/8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/.system_generated/tasks/task-13.log
</SYSTEM_MESSAGE>

Created At: 2026-08-10T19:52:47-07:00
Tool is running as a background task with task id: 8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-22
Task Description: python -c "import sys; sys.path.insert(0, r'p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF'); import wrapper; print('wrapper imported successfully')"
Task logs are available at: file:///C:/Users/blibd/.gemini/antigravity/brain/8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/.system_generated/tasks/task-22.log

Created At: 2026-08-10T19:52:58-07:00
Completed At: 2026-08-10T19:52:59-07:00
Task: 8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-22
Status: RUNNING
Log: C:\Users\blibd\.gemini\antigravity\brain\8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad\.system_generated\tasks\task-22.log
Log output:
Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.

Last progress: 2s ago


REMINDER: Do not call this tool again to poll or wait for updates. You will be automatically notified when the task completes or a message arrives. If you need a bounded wait, use the `schedule` tool -- it waits silently in the background and suppresses its notification if you are woken by another event.

Created At: 2026-08-10T19:53:01-07:00
Completed At: 2026-08-10T19:53:01-07:00
File Path: `file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/custom_nodes/Comfy-CMF/wrapper.py`
Total Lines: 338
Total Bytes: 13385
Showing lines 1 to 338
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import ctypes
2: import os
3: import sys
4: import json
5: from pathlib import Path
6: import numpy as np
7: import torch
8: 
9: 
10: class CMFWrapper:
11:     """
12:     Python ctypes wrapper for the CMF (Cortiq Model Format) Rust FFI library (cortiq-ffi).
13:     Manages loading the native dynamic library, defining C ABI signatures, GPU toggles, and error inspection.
14:     """
15:     
16:     def __init__(self, lib_path=None):
17:         if lib_path is None:
18:             lib_path = self._find_library()
19:             
20:         if not os.path.exists(lib_path):
21:             raise FileNotFoundError(
22:                 f"[ComfyUI-CMF] Shared library not found at: '{lib_path}'. "
23:                 "Please place cortiq_ffi.dll (Windows), libcortiq_ffi.so (Linux), or "
24:                 "libcortiq_ffi.dylib (macOS) in the 'bin/' directory, or build using "
25:                 "'cargo build -p cortiq-ffi --release'."
26:             )
27:             
28:         try:
29:             self.lib = ctypes.CDLL(lib_path)
30:         except Exception as e:
31:             raise RuntimeError(f"[ComfyUI-CMF] Failed to load dynamic library '{lib_path}': {e}")
32:             
33:         self._bind_signatures()
34: 
35:     def _find_library(self) -> str:
36:         """Dynamically detect host OS and locate cortiq_ffi dynamic library."""
37:         base_dir = Path(__file__).parent / "bin"
38:         
39:         if sys.platform == "win32":
40:             lib_name = "cortiq_ffi.dll"
41:         elif sys.platform == "darwin":
42:             lib_name = "libcortiq_ffi.dylib"
43:         else:
44:             lib_name = "libcortiq_ffi.so"
45:             
46:         target = base_dir / lib_name
47:         if target.exists():
48:             return str(target)
49:             
50:         alt_target = Path(__file__).parent / lib_name
51:         if alt_target.exists():
52:             return str(alt_target)
53:             
54:         return str(target)
55: 
56:     def _bind_signatures(self):
57:         """Bind C ABI function signatures matching cortiq.h."""
58:         # void *cortiq_load(const char *path);
59:         self.lib.cortiq_load.restype = ctypes.c_void_p
60:         self.lib.cortiq_load.argtypes = [ctypes.c_char_p]
61:         
62:         # void cortiq_set_gpu(bool enable);
63:         if hasattr(self.lib, "cortiq_set_gpu"):
64:             self.lib.cortiq_set_gpu.restype = None
65:             self.lib.cortiq_set_gpu.argtypes = [ctypes.c_bool]
66:             
67:         # void cortiq_set_threads(int32_t n);
68:         if hasattr(self.lib, "cortiq_set_threads"):
69:             self.lib.cortiq_set_threads.restype = None
70:             self.lib.cortiq_set_threads.argtypes = [ctypes.c_int32]
71:             
72:         # int32_t cortiq_set_options(void *handle, const char *json_options);
73:         self.lib.cortiq_set_options.restype = ctypes.c_int32
74:         self.lib.cortiq_set_options.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
75:         
76:         # typedef bool (*cortiq_token_cb)(const char *token, void *user);
77:         self.CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_char_p, ctypes.c_void_p)
78:         
79:         # int32_t cortiq_chat(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);
80:         self.lib.cortiq_chat.restype = ctypes.c_int32
81:         self.lib.cortiq_chat.argtypes = [
82:             ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
83:             self.CALLBACK_TYPE, ctypes.c_void_p
84:         ]
85: 
86:         # int32_t cortiq_chat_messages(void *handle, const char *json_messages, uint32_t max_tokens, cortiq_token_cb cb, void *user);
87:         if hasattr(self.lib, "cortiq_chat_messages"):
88:             self.lib.cortiq_chat_messages.restype = ctypes.c_int32
89:             self.lib.cortiq_chat_messages.argtypes = [
90:                 ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
91:                 self.CALLBACK_TYPE, ctypes.c_void_p
92:             ]
93:         
94:         # typedef bool (*cortiq_progress_cb)(uint32_t step, uint32_t total_steps, void *user);
95:         self.PROGRESS_CALLBACK_TYPE = ctypes.CFUNCTYPE(
96:             ctypes.c_bool, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p
97:         )
98: 
99:         # int32_t cortiq_imagine(
100:         #     const char *model_path, const char *prompt,
101:         #     uint32_t width, uint32_t height, uint32_t steps,
102:         #     float guidance, uint64_t seed, uint8_t *out_rgb,
103:         #     cortiq_progress_cb progress, void *user
104:         # );
105:         if hasattr(self.lib, "cortiq_imagine"):
106:             self.lib.cortiq_imagine.restype = ctypes.c_int32
107:             self.lib.cortiq_imagine.argtypes = [
108:                 ctypes.c_char_p,
109:                 ctypes.c_char_p,
110:                 ctypes.c_uint32,
111:                 ctypes.c_uint32,
112:                 ctypes.c_uint32,
113:                 ctypes.c_float,
114:                 ctypes.c_uint64,
115:                 ctypes.POINTER(ctypes.c_uint8),
116:                 self.PROGRESS_CALLBACK_TYPE,
117:                 ctypes.c_void_p,
118:             ]
119: 
120:         
121:         # void cortiq_cancel(void *handle);
122:         if hasattr(self.lib, "cortiq_cancel"):
123:             self.lib.cortiq_cancel.restype = None
124:             self.lib.cortiq_cancel.argtypes = [ctypes.c_void_p]
125:             
126:         # const char *cortiq_last_error(void);
127:         if hasattr(self.lib, "cortiq_last_error"):
128:             self.lib.cortiq_last_error.restype = ctypes.c_char_p
129:             self.lib.cortiq_last_error.argtypes = []
130: 
131:         # const char *cortiq_execution_info(void);
132:         if hasattr(self.lib, "cortiq_execution_info"):
133:             self.lib.cortiq_execution_info.restype = ctypes.c_char_p
134:             self.lib.cortiq_execution_info.argtypes = []
135: 
136:         # void cortiq_free(void *handle);
137:         self.lib.cortiq_free.restype = None
138:         self.lib.cortiq_free.argtypes = [ctypes.c_void_p]
139: 
140:     def set_gpu(self, enable: bool = True):
141:         """Enable or disable discrete GPU graph acceleration (Vulkan / Metal). Must be called before load."""
142:         if hasattr(self.lib, "cortiq_set_gpu"):
143:             self.lib.cortiq_set_gpu(enable)
144: 
145:     def set_threads(self, num_threads: int = 0):
146:         """Set execution thread pool count (0 = automatic based on physical CPU cores)."""
147:         if hasattr(self.lib, "cortiq_set_threads"):
148:             self.lib.cortiq_set_threads(num_threads)
149: 
150:     def get_last_error(self) -> str:
151:         """Extract thread-local diagnostic error string from C runtime."""
152:         if hasattr(self.lib, "cortiq_last_error"):
153:             err_ptr = self.lib.cortiq_last_error()
154:             if err_ptr:
155:                 return ctypes.string_at(err_ptr).decode("utf-8", errors="replace")
156:         return "Unknown CMF FFI error"
157: 
158:     def get_execution_info(self) -> str:
159:         """Query execution environment info JSON."""
160:         if hasattr(self.lib, "cortiq_execution_info"):
161:             info_ptr = self.lib.cortiq_execution_info()
162:             if info_ptr:
163:                 return ctypes.string_at(info_ptr).decode("utf-8", errors="replace")
164:         return "{}"
165: 
166:     def load_model(self, model_path: str, enable_gpu: bool = True, num_threads: int = 0):
167:         """Memory-map and open a .cmf model file, returning a CMFModelHandle."""
168:         if not os.path.exists(model_path):
169:             raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
170:             
171:         self.set_gpu(enable_gpu)
172:         self.set_threads(num_threads)
173:         
174:         handle = self.lib.cortiq_load(model_path.encode("utf-8"))
175:         if not handle:
176:             err = self.get_last_error()
177:             raise RuntimeError(f"[ComfyUI-CMF] Failed to load model '{model_path}': {err}")
178:             
179:         return CMFModelHandle(self, handle, model_path)
180: 
181:     def generate_image(
182:         self,
183:         model_path: str,
184:         prompt: str,
185:         width: int,
186:         height: int,
187:         steps: int,
188:         guidance: float,
189:         seed: int,
190:         enable_gpu: bool = True,
191:         num_threads: int = 0,
192:         interrupt_check_fn=None,
193:     ) -> torch.Tensor:
194:         """
195:         Generate an image using cortiq_imagine Rust FFI binding.
196:         Allocates uint8 RGB numpy array, populates via C-FFI, and returns float32 PyTorch tensor [1, H, W, 3] normalized in [0.0, 1.0].
197:         """
198:         if not os.path.exists(model_path):
199:             raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
200: 
201:         if not hasattr(self.lib, "cortiq_imagine"):
202:             raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_imagine support.")
203: 
204:         self.set_gpu(enable_gpu)
205:         self.set_threads(num_threads)
206: 
207:         rgb_np = np.zeros((height, width, 3), dtype=np.uint8)
208:         out_ptr = rgb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
209: 
210:         def py_progress_cb(step, total_steps, user_data):
211:             if interrupt_check_fn and interrupt_check_fn():
212:                 return False
213:             return True
214: 
215:         c_progress_cb = self.PROGRESS_CALLBACK_TYPE(py_progress_cb)
216: 
217:         res = self.lib.cortiq_imagine(
218:             model_path.encode("utf-8"),
219:             prompt.encode("utf-8"),
220:             int(width),
221:             int(height),
222:             int(steps),
223:             float(guidance),
224:             int(seed),
225:             out_ptr,
226:             c_progress_cb,
227:             None,
228:         )
229: 
230:         if res < 0:
231:             err = self.get_last_error()
232:             raise RuntimeError(f"[ComfyUI-CMF] Image generation failed: {err}")
233: 
234:         image_tensor = torch.from_numpy(rgb_np).to(torch.float32) / 255.0
235:         return image_tensor.unsqueeze(0)
236: 
237: 
238: 
239: class CMFModelHandle:
240:     """
241:     RAII wrapper around CMF opaque void* model handles.
242:     Ensures memory-mapped files and C memory structures are freed via cortiq_free.
243:     """
244:     
245:     def __init__(self, wrapper: CMFWrapper, handle: int, path: str):
246:         self.wrapper = wrapper
247:         self.handle = handle
248:         self.path = path
249:         self._closed = False
250: 
251:     def set_options(self, options_dict: dict):
252:         """Serialize sampler options to JSON and pass to Rust runtime."""
253:         if self._closed or not self.handle:
254:             raise RuntimeError("[ComfyUI-CMF] Attempted to set options on closed model handle.")
255:             
256:         opt_json = json.dumps(options_dict).encode("utf-8")
257:         res = self.wrapper.lib.cortiq_set_options(self.handle, opt_json)
258:         if res != 0:
259:             err = self.wrapper.get_last_error()
260:             raise RuntimeError(f"[ComfyUI-CMF] Failed to set options: {err}")
261: 
262:     def generate(self, prompt: str, max_tokens: int, interrupt_check_fn=None) -> str:
263:         """
264:         Execute single-turn streaming prompt generation.
265:         Checks interrupt_check_fn periodically and invokes cortiq_cancel if requested.
266:         """
267:         if self._closed or not self.handle:
268:             raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
269:             
270:         output_tokens = []
271:         
272:         def py_callback(token_ptr, user_data):
273:             if interrupt_check_fn and interrupt_check_fn():
274:                 if hasattr(self.wrapper.lib, "cortiq_cancel"):
275:                     self.wrapper.lib.cortiq_cancel(self.handle)
276:                 return False
277:                 
278:             if token_ptr:
279:                 token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
280:                 output_tokens.append(token_str)
281:             return True
282: 
283:         c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
284:         
285:         res = self.wrapper.lib.cortiq_chat(
286:             self.handle, prompt.encode("utf-8"), max_tokens, c_callback, None
287:         )
288:         
289:         if res < 0:
290:             err = self.wrapper.get_last_error()
291:             raise RuntimeError(f"[ComfyUI-CMF] Text generation failed: {err}")
292:             
293:         return "".join(output_tokens)
294: 
295:     def generate_messages(self, messages_list: list, max_tokens: int, interrupt_check_fn=None) -> str:
296:         """Execute multi-turn chat template generation using cortiq_chat_messages."""
297:         if self._closed or not self.handle:
298:             raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
299:             
300:         if not hasattr(self.wrapper.lib, "cortiq_chat_messages"):
301:             raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_chat_messages support.")
302:             
303:         output_tokens = []
304:         
305:         def py_callback(token_ptr, user_data):
306:             if interrupt_check_fn and interrupt_check_fn():
307:                 if hasattr(self.wrapper.lib, "cortiq_cancel"):
308:                     self.wrapper.lib.cortiq_cancel(self.handle)
309:                 return False
310:                 
311:             if token_ptr:
312:                 token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
313:                 output_tokens.append(token_str)
314:             return True
315: 
316:         c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
317:         msgs_json = json.dumps(messages_list).encode("utf-8")
318:         
319:         res = self.wrapper.lib.cortiq_chat_messages(
320:             self.handle, msgs_json, max_tokens, c_callback, None
321:         )
322:         
323:         if res < 0:
324:             err = self.wrapper.get_last_error()
325:             raise RuntimeError(f"[ComfyUI-CMF] Chat messages generation failed: {err}")
326:             
327:         return "".join(output_tokens)
328: 
329:     def close(self):
330:         """Explicitly release Rust model handle and unmap memory."""
331:         if not self._closed and self.handle:
332:             self.wrapper.lib.cortiq_free(self.handle)
333:             self.handle = None
334:             self._closed = True
335: 
336:     def __del__(self):
337:         self.close()
338: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-10T19:53:04-07:00
Completed At: 2026-08-10T19:53:04-07:00
Message sent to "b8888b03-2e45-47f5-96ec-b7096fc06bc6".

The following is a <SYSTEM_MESSAGE> not actually sent by the user. It is provided by the system as important information to pay attention to.

<SYSTEM_MESSAGE>
[Message] timestamp=2026-08-11T02:53:03Z sender=8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-22 priority=MESSAGE_PRIORITY_HIGH content=Task id "8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/task-22" finished with result:

				The command exited with code 0.
				Output:
				Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.
wrapper imported successfully


Log: file:///C:/Users/blibd/.gemini/antigravity/brain/8aaffcc8-d2e2-4d48-b7a6-3ffacf36b0ad/.system_generated/tasks/task-22.log
</SYSTEM_MESSAGE>

I have completed the task to update [`wrapper.py`](file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/custom_nodes/Comfy-CMF/wrapper.py).

### Work Completed:
1. **Added NumPy and PyTorch imports**:
   - Added `import numpy as np` and `import torch` to [`wrapper.py`](file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/custom_nodes/Comfy-CMF/wrapper.py).

2. **C-FFI Progress Callback & Binding**:
   - Defined `PROGRESS_CALLBACK_TYPE` matching `typedef bool (*cortiq_progress_cb)(uint32_t step, uint32_t total_steps, void *user)`.
   - Bound `cortiq_imagine` in `CMFWrapper._bind_signatures()`:
     ```c
     int32_t cortiq_imagine(
         const char *model_path, const char *prompt,
         uint32_t width, uint32_t height, uint32_t steps,
         float guidance, uint64_t seed, uint8_t *out_rgb,
         cortiq_progress_cb progress, void *user
     );
     ```

3. **Implemented `generate_image` method in `CMFWrapper`**:
   - `generate_image(model_path, prompt, width, height, steps, guidance, seed, enable_gpu=True, num_threads=0, interrupt_check_fn=None)`
   - Allocates `rgb_np = np.zeros((height, width, 3), dtype=np.uint8)`.
   - Passes `rgb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))` to `cortiq_imagine`.
   - Checks return status and converts the uint8 numpy array to a float32 PyTorch tensor normalized in `[0.0, 1.0]` with shape `[1, height, width, 3]`.

---
