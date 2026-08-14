# Conversation Archive: Subagent 05: Rust cortiq-ffi Release GPU Cargo Build

- **Session ID**: `2237c28f-cf74-4d36-b556-809a825fc7ea`
- **Role**: Rust Build Engineer
- **Type**: Subagent
- **Total Turns**: 1
- **Timeline**: 2026-08-11T22:35:19Z to 2026-08-11T22:35:19Z

---

## Turn 1 (Step 0)
*Timestamp: 2026-08-11T22:35:19Z*

### 👤 User
Rebuild cortiq-ffi in release GPU mode via cargo build -p cortiq-ffi --release --features gpu once gpu_wgpu.rs changes are complete and copy cortiq_ffi.dll to p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\bin\cortiq_ffi.dll.

### ⚙️ Actions & Tool Execution
<details>
<summary>Executed Tools and Actions (22 actions)</summary>

- **`view_file`**: view_file — Viewed ``
- **`find_by_name`**: find_by_name
- **`find_by_name`**: find_by_name
- **`manage_task`**: manage_task
- **`grep_search`**: grep_search
- **`grep_search`**: grep_search
- **`find_by_name`**: find_by_name
- **`view_file`**: view_file — Viewed ``
- **`run_command`**: run_command
- **`find_by_name`**: find_by_name
- **`run_command`**: run_command
- **`manage_task`**: manage_task
- **`find_by_name`**: find_by_name
- **`run_command`**: run_command
- **`view_file`**: view_file — Viewed ``
- **`view_file`**: view_file — Viewed ``
- **`run_command`**: run_command
- **`view_file`**: view_file — Viewed ``
- **`run_command`**: run_command
- **`view_file`**: view_file — Viewed ``
- **`manage_task`**: manage_task
- **`send_message`**: send_message

</details>

### 🤖 Assistant
Created At: 2026-08-11T15:35:20-07:00
Completed At: 2026-08-11T15:35:21-07:00
File Path: `file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/custom_nodes/Comfy-CMF/wrapper.py`
Total Lines: 356
Total Bytes: 13993
Showing lines 1 to 356
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
46:         # Check compiled GPU release target in cmf_source first
47:         build_target = Path(__file__).parent.parent.parent / "cmf_source" / "target" / "release" / lib_name
48:         if build_target.exists():
49:             return str(build_target)
50:             
51:         base_dir = Path(__file__).parent / "bin"
52:         target = base_dir / lib_name
53:         if target.exists():
54:             return str(target)
55:             
56:         alt_target = Path(__file__).parent / lib_name
57:         if alt_target.exists():
58:             return str(alt_target)
59: 
60:             
61:         return str(target)
62: 
63:     def _bind_signatures(self):
64:         """Bind C ABI function signatures matching cortiq.h."""
65:         # void *cortiq_load(const char *path);
66:         self.lib.cortiq_load.restype = ctypes.c_void_p
67:         self.lib.cortiq_load.argtypes = [ctypes.c_char_p]
68:         
69:         # void cortiq_set_gpu(bool enable);
70:         if hasattr(self.lib, "cortiq_set_gpu"):
71:             self.lib.cortiq_set_gpu.restype = None
72:             self.lib.cortiq_set_gpu.argtypes = [ctypes.c_bool]
73:             
74:         # void cortiq_set_threads(int32_t n);
75:         if hasattr(self.lib, "cortiq_set_threads"):
76:             self.lib.cortiq_set_threads.restype = None
77:             self.lib.cortiq_set_threads.argtypes = [ctypes.c_int32]
78:             
79:         # int32_t cortiq_set_options(void *handle, const char *json_options);
80:         self.lib.cortiq_set_options.restype = ctypes.c_int32
81:         self.lib.cortiq_set_options.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
82:         
83:         # typedef bool (*cortiq_token_cb)(const char *token, void *user);
84:         self.CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_char_p, ctypes.c_void_p)
85:         
86:         # int32_t cortiq_chat(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);
87:         self.lib.cortiq_chat.restype = ctypes.c_int32
88:         self.lib.cortiq_chat.argtypes = [
89:             ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
90:             self.CALLBACK_TYPE, ctypes.c_void_p
91:         ]
92: 
93:         # int32_t cortiq_chat_messages(void *handle, const char *json_messages, uint32_t max_tokens, cortiq_token_cb cb, void *user);
94:         if hasattr(self.lib, "cortiq_chat_messages"):
95:             self.lib.cortiq_chat_messages.restype = ctypes.c_int32
96:             self.lib.cortiq_chat_messages.argtypes = [
97:                 ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
98:                 self.CALLBACK_TYPE, ctypes.c_void_p
99:             ]
100:         
101:         # typedef bool (*cortiq_progress_cb)(uint32_t step, uint32_t total_steps, void *user);
102:         self.PROGRESS_CALLBACK_TYPE = ctypes.CFUNCTYPE(
103:             ctypes.c_bool, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p
104:         )
105: 
106:         # int32_t cortiq_imagine(
107:         #     const char *model_path, const char *prompt,
108:         #     uint32_t width, uint32_t height, uint32_t steps,
109:         #     float guidance, uint64_t seed, uint8_t *out_rgb,
110:         #     cortiq_progress_cb progress, void *user
111:         # );
112:         if hasattr(self.lib, "cortiq_imagine"):
113:             self.lib.cortiq_imagine.restype = ctypes.c_int32
114:             self.lib.cortiq_imagine.argtypes = [
115:                 ctypes.c_char_p,
116:                 ctypes.c_char_p,
117:                 ctypes.c_uint32,
118:                 ctypes.c_uint32,
119:                 ctypes.c_uint32,
120:                 ctypes.c_float,
121:                 ctypes.c_uint64,
122:                 ctypes.POINTER(ctypes.c_uint8),
123:                 self.PROGRESS_CALLBACK_TYPE,
124:                 ctypes.c_void_p,
125:             ]
126: 
127:         
128:         # void cortiq_cancel(void *handle);
129:         if hasattr(self.lib, "cortiq_cancel"):
130:             self.lib.cortiq_cancel.restype = None
131:             self.lib.cortiq_cancel.argtypes = [ctypes.c_void_p]
132:             
133:         # const char *cortiq_last_error(void);
134:         if hasattr(self.lib, "cortiq_last_error"):
135:             self.lib.cortiq_last_error.restype = ctypes.c_char_p
136:             self.lib.cortiq_last_error.argtypes = []
137: 
138:         # const char *cortiq_execution_info(void);
139:         if hasattr(self.lib, "cortiq_execution_info"):
140:             self.lib.cortiq_execution_info.restype = ctypes.c_char_p
141:             self.lib.cortiq_execution_info.argtypes = []
142: 
143:         # void cortiq_free(void *handle);
144:         self.lib.cortiq_free.restype = None
145:         self.lib.cortiq_free.argtypes = [ctypes.c_void_p]
146: 
147:     def set_gpu(self, enable: bool = True):
148:         """Enable or disable discrete GPU graph acceleration (Vulkan / Metal). Must be called before load."""
149:         if hasattr(self.lib, "cortiq_set_gpu"):
150:             self.lib.cortiq_set_gpu(enable)
151: 
152:     def set_threads(self, num_threads: int = 0):
153:         """Set execution thread pool count (0 = automatic based on physical CPU cores)."""
154:         if hasattr(self.lib, "cortiq_set_threads"):
155:             self.lib.cortiq_set_threads(num_threads)
156: 
157:     def get_last_error(self) -> str:
158:         """Extract thread-local diagnostic error string from C runtime."""
159:         if hasattr(self.lib, "cortiq_last_error"):
160:             err_ptr = self.lib.cortiq_last_error()
161:             if err_ptr:
162:                 return ctypes.string_at(err_ptr).decode("utf-8", errors="replace")
163:         return "Unknown CMF FFI error"
164: 
165:     def get_execution_info(self) -> str:
166:         """Query execution environment info JSON."""
167:         if hasattr(self.lib, "cortiq_execution_info"):
168:             info_ptr = self.lib.cortiq_execution_info()
169:             if info_ptr:
170:                 return ctypes.string_at(info_ptr).decode("utf-8", errors="replace")
171:         return "{}"
172: 
173:     def load_model(self, model_path: str, enable_gpu: bool = True, num_threads: int = 0):
174:         """Memory-map and open a .cmf model file, returning a CMFModelHandle."""
175:         if not os.path.exists(model_path):
176:             raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
177:             
178:         self.set_gpu(enable_gpu)
179:         self.set_threads(num_threads)
180:         
181:         handle = self.lib.cortiq_load(model_path.encode("utf-8"))
182:         if not handle:
183:             err = self.get_last_error()
184:             raise RuntimeError(f"[ComfyUI-CMF] Failed to load model '{model_path}': {err}")
185:             
186:         return CMFModelHandle(self, handle, model_path)
187: 
188:     def generate_image(
189:         self,
190:         model_path: str,
191:         prompt: str,
192:         width: int,
193:         height: int,
194:         steps: int,
195:         guidance: float,
196:         seed: int,
197:         enable_gpu: bool = True,
198:         num_threads: int = 0,
199:         interrupt_check_fn=None,
200:         progress_callback=None,
201:     ) -> torch.Tensor:
202:         """
203:         Generate an image using cortiq_imagine Rust FFI binding.
204:         Allocates uint8 RGB numpy array, populates via C-FFI, and returns float32 PyTorch tensor [1, H, W, 3] normalized in [0.0, 1.0].
205:         """
206:         if not os.path.exists(model_path):
207:             raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
208: 
209:         if not hasattr(self.lib, "cortiq_imagine"):
210:             raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_imagine support.")
211: 
212:         self.set_gpu(enable_gpu)
213:         self.set_threads(num_threads)
214:         if enable_gpu:
215:             os.environ["CMF_GPU"] = "1"
216:             os.environ["CMF_GPU_PROBE"] = "0"
217: 
218:         rgb_np = np.zeros((height, width, 3), dtype=np.uint8)
219: 
220:         out_ptr = rgb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
221: 
222:         def py_progress_cb(step, total_steps, user_data):
223:             if progress_callback:
224:                 try:
225:                     progress_callback(step, total_steps)
226:                 except Exception:
227:                     pass
228:             if interrupt_check_fn and interrupt_check_fn():
229:                 return False
230:             return True
231: 
232: 
233:         c_progress_cb = self.PROGRESS_CALLBACK_TYPE(py_progress_cb)
234: 
235:         res = self.lib.cortiq_imagine(
236:             model_path.encode("utf-8"),
237:             prompt.encode("utf-8"),
238:             int(width),
239:             int(height),
240:             int(steps),
241:             float(guidance),
242:             int(seed),
243:             out_ptr,
244:             c_progress_cb,
245:             None,
246:         )
247: 
248:         if res < 0:
249:             err = self.get_last_error()
250:             raise RuntimeError(f"[ComfyUI-CMF] Image generation failed: {err}")
251: 
252:         image_tensor = torch.from_numpy(rgb_np).to(torch.float32) / 255.0
253:         return image_tensor.unsqueeze(0)
254: 
255: 
256: 
257: class CMFModelHandle:
258:     """
259:     RAII wrapper around CMF opaque void* model handles.
260:     Ensures memory-mapped files and C memory structures are freed via cortiq_free.
261:     """
262:     
263:     def __init__(self, wrapper: CMFWrapper, handle: int, path: str):
264:         self.wrapper = wrapper
265:         self.handle = handle
266:         self.path = path
267:         self._closed = False
268: 
269:     def set_options(self, options_dict: dict):
270:         """Serialize sampler options to JSON and pass to Rust runtime."""
271:         if self._closed or not self.handle:
272:             raise RuntimeError("[ComfyUI-CMF] Attempted to set options on closed model handle.")
273:             
274:         opt_json = json.dumps(options_dict).encode("utf-8")
275:         res = self.wrapper.lib.cortiq_set_options(self.handle, opt_json)
276:         if res != 0:
277:             err = self.wrapper.get_last_error()
278:             raise RuntimeError(f"[ComfyUI-CMF] Failed to set options: {err}")
279: 
280:     def generate(self, prompt: str, max_tokens: int, interrupt_check_fn=None) -> str:
281:         """
282:         Execute single-turn streaming prompt generation.
283:         Checks interrupt_check_fn periodically and invokes cortiq_cancel if requested.
284:         """
285:         if self._closed or not self.handle:
286:             raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
287:             
288:         output_tokens = []
289:         
290:         def py_callback(token_ptr, user_data):
291:             if interrupt_check_fn and interrupt_check_fn():
292:                 if hasattr(self.wrapper.lib, "cortiq_cancel"):
293:                     self.wrapper.lib.cortiq_cancel(self.handle)
294:                 return False
295:                 
296:             if token_ptr:
297:                 token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
298:                 output_tokens.append(token_str)
299:             return True
300: 
301:         c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
302:         
303:         res = self.wrapper.lib.cortiq_chat(
304:             self.handle, prompt.encode("utf-8"), max_tokens, c_callback, None
305:         )
306:         
307:         if res < 0:
308:             err = self.wrapper.get_last_error()
309:             raise RuntimeError(f"[ComfyUI-CMF] Text generation failed: {err}")
310:             
311:         return "".join(output_tokens)
312: 
313:     def generate_messages(self, messages_list: list, max_tokens: int, interrupt_check_fn=None) -> str:
314:         """Execute multi-turn chat template generation using cortiq_chat_messages."""
315:         if self._closed or not self.handle:
316:             raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
317:             
318:         if not hasattr(self.wrapper.lib, "cortiq_chat_messages"):
319:             raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_chat_messages support.")
320:             
321:         output_tokens = []
322:         
323:         def py_callback(token_ptr, user_data):
324:             if interrupt_check_fn and interrupt_check_fn():
325:                 if hasattr(self.wrapper.lib, "cortiq_cancel"):
326:                     self.wrapper.lib.cortiq_cancel(self.handle)
327:                 return False
328:                 
329:             if token_ptr:
330:                 token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
331:                 output_tokens.append(token_str)
332:             return True
333: 
334:         c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
335:         msgs_json = json.dumps(messages_list).encode("utf-8")
336:         
337:         res = self.wrapper.lib.cortiq_chat_messages(
338:             self.handle, msgs_json, max_tokens, c_callback, None
339:         )
340:         
341:         if res < 0:
342:             err = self.wrapper.get_last_error()
343:             raise RuntimeError(f"[ComfyUI-CMF] Chat messages generation failed: {err}")
344:             
345:         return "".join(output_tokens)
346: 
347:     def close(self):
348:         """Explicitly release Rust model handle and unmap memory."""
349:         if not self._closed and self.handle:
350:             self.wrapper.lib.cortiq_free(self.handle)
351:             self.handle = None
352:             self._closed = True
353: 
354:     def __del__(self):
355:         self.close()
356: 
The above content shows the entire, complete file contents of the requested file.

{{ CHECKPOINT 0 }}
 **The earlier parts of this conversation have been truncated due to its long length. The following content summarizes the truncated context so that you may continue your work. **


# USER Objective:
Rebuild And Deploy Cortiq-FFI

# User Requests
The following were user requests from the truncated conversation in chronological order:
1. Rebuild cortiq-ffi in release GPU mode via cargo build -p cortiq-ffi --release --features gpu once gpu_wgpu.rs changes are complete and copy cortiq_ffi.dll to p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\bin\cortiq_ffi.dll.

# Conversation Logs

Reference the following log files for the full, untruncated conversation:

- C:\Users\blibd\.gemini\antigravity\brain\2237c28f-cf74-4d36-b556-809a825fc7ea\.system_generated\logs\transcript.jsonl

**IMPORTANT: this summary is just for your reference. You may respond to my previous and future messages, but DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE. JUST READ IT BUT DO NOT MENTION IT, RESPOND TO IT, OR TAKE ACTION BECAUSE OF IT.**

Created At: 2026-08-11T15:35:22-07:00
Completed At: 2026-08-11T15:35:23-07:00
Found 7 results
cmf_source/Cargo.toml
cmf_source/crates/cortiq-cli/Cargo.toml
cmf_source/crates/cortiq-core/Cargo.toml
cmf_source/crates/cortiq-engine/Cargo.toml
cmf_source/crates/cortiq-ffi/Cargo.toml
cmf_source/crates/cortiq-server/Cargo.toml
cmf_source/tools/vkcoop/Cargo.toml

Created At: 2026-08-11T15:35:24-07:00
Completed At: 2026-08-11T15:35:24-07:00
Found 81 results
crates/cortiq-engine/examples/q4tp_gpu_ab.rs
crates/cortiq-engine/src/gpu.rs
crates/cortiq-engine/src/gpu_metal.rs
crates/cortiq-engine/src/gpu_wgpu.rs
crates/cortiq-engine/tests/gpu_attend_parity.rs
crates/cortiq-engine/tests/gpu_axpy_parity.rs
crates/cortiq-engine/tests/gpu_bt_route_parity.rs
crates/cortiq-engine/tests/gpu_compress_parity.rs
crates/cortiq-engine/tests/gpu_dsv4_frame.rs
crates/cortiq-engine/tests/gpu_gemm_scratch.rs
crates/cortiq-engine/tests/gpu_hc_parity.rs
crates/cortiq-engine/tests/gpu_micro.rs
crates/cortiq-engine/tests/gpu_mv4b_parity.rs
crates/cortiq-engine/tests/gpu_olora_parity.rs
crates/cortiq-engine/tests/gpu_q4t_bench.rs
crates/cortiq-engine/tests/gpu_q4t_mm.rs
crates/cortiq-engine/tests/gpu_q4t_mm_wgpu.rs
crates/cortiq-engine/tests/gpu_q4tp.rs
crates/cortiq-engine/tests/gpu_q4tp_batch.rs
crates/cortiq-engine/tests/gpu_q4tp_parity.rs
crates/cortiq-engine/tests/gpu_rope_parity.rs
crates/cortiq-engine/tests/gpu_route_parity.rs
crates/cortiq-engine/tests/gpu_spec_buf_diff.rs
crates/cortiq-engine/tests/gpu_spec_txn.rs
target/debug/deps/gpu_attend_parity-484a00ce89c9136f.d
target/debug/deps/gpu_attend_parity-484a00ce89c9136f.exe
target/debug/deps/gpu_attend_parity-484a00ce89c9136f.pdb
target/debug/deps/gpu_axpy_parity-3db6a2ec19c4648f.d
target/debug/deps/gpu_axpy_parity-3db6a2ec19c4648f.exe
target/debug/deps/gpu_axpy_parity-3db6a2ec19c4648f.pdb
target/debug/deps/gpu_bt_route_parity-d167e13ed8c52005.d
target/debug/deps/gpu_bt_route_parity-d167e13ed8c52005.exe
target/debug/deps/gpu_bt_route_parity-d167e13ed8c52005.pdb
target/debug/deps/gpu_compress_parity-d84b0a29927a2bc7.d
target/debug/deps/gpu_compress_parity-d84b0a29927a2bc7.exe
target/debug/deps/gpu_compress_parity-d84b0a29927a2bc7.pdb
target/debug/deps/gpu_dsv4_frame-564bf773ee3ae6a4.d
target/debug/deps/gpu_dsv4_frame-564bf773ee3ae6a4.exe
target/debug/deps/gpu_dsv4_frame-564bf773ee3ae6a4.pdb
target/debug/deps/gpu_gemm_scratch-552193602f58bd91.d
target/debug/deps/gpu_gemm_scratch-552193602f58bd91.exe
target/debug/deps/gpu_gemm_scratch-552193602f58bd91.pdb
target/debug/deps/gpu_hc_parity-a0d0c346cc47b373.d
target/debug/deps/gpu_hc_parity-a0d0c346cc47b373.exe
target/debug/deps/gpu_hc_parity-a0d0c346cc47b373.pdb
target/debug/deps/gpu_micro-9bf63f03e0ef6213.d
target/debug/deps/gpu_micro-9bf63f03e0ef6213.exe
target/debug/deps/gpu_micro-9bf63f03e0ef6213.pdb
target/debug/deps/gpu_mv4b_parity-fca3d3a850a3383b.d
target/debug/deps/gpu_mv4b_parity-fca3d3a850a3383b.exe
(...31 more results not shown)

Created At: 2026-08-11T15:35:24-07:00
Completed At: 2026-08-11T15:35:24-07:00
No background tasks are currently running.

Created At: 2026-08-11T15:35:29-07:00
Completed At: 2026-08-11T15:35:29-07:00
Found 2 results
src/lib.rs
tests/e2e.rs

Created At: 2026-08-11T15:35:29-07:00
Completed At: 2026-08-11T15:35:30-07:00
File Path: `file:///p:/Downloaded/ComfyUI_windows_portable/ComfyUI/cmf_source/crates/cortiq-ffi/src/lib.rs`
Total Lines: 604
Total Bytes: 21727
Showing lines 1 to 604
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: //! C ABI over the CMF runtime — the embedding surface for mobile apps
2: //! (Android JNI / iOS / desktop FFI). Design rules:
3: //! - opaque handle, every call goes through a Mutex (the engine is
4: //!   single-stream; callers may invoke from any thread, one at a time);
5: //! - no panics across the boundary (catch_unwind on every entry);
6: //! - errors are a thread-local UTF-8 string behind `cortiq_last_error`;
7: //! - streaming via a C callback returning `true` to continue — early
8: //!   stop is first-class, matching the engine's own TokenCallback.
9: // The entry points take raw pointers from a foreign caller by design;
10: // each one NULL-checks before dereferencing. Marking them `unsafe`
11: // would change nothing for C callers and only obscure the Rust tests.
12: #![allow(clippy::not_unsafe_ptr_arg_deref)]
13: 
14: use std::ffi::{CStr, CString, c_char, c_void};
15: use std::panic::{AssertUnwindSafe, catch_unwind};
16: use std::sync::{Arc, Mutex};
17: 
18: use cortiq_core::CmfModel;
19: use cortiq_engine::{Pipeline, SamplerConfig};
20: 
21: struct Ctx {
22:     pipeline: Mutex<Pipeline>,
23:     /// Clone of the pipeline's cancel flag — reachable while the
24:     /// pipeline mutex is held by a running generation.
25:     cancel: std::sync::Arc<std::sync::atomic::AtomicBool>,
26:     /// Sticky `enable_thinking` for reasoning-model chat templates
27:     /// (Qwen3/3.5): `None` leaves it undefined so the template picks its own
28:     /// default; `Some(false)` makes the model answer directly instead of
29:     /// emitting a `<think>` block. Set through `cortiq_set_options`.
30:     enable_thinking: Mutex<Option<bool>>,
31: }
32: 
33: thread_local! {
34:     static LAST_ERROR: std::cell::RefCell<CString> =
35:         std::cell::RefCell::new(CString::new("").unwrap());
36: }
37: 
38: fn set_error(msg: &str) {
39:     let clean = msg.replace('\0', " ");
40:     LAST_ERROR.with(|e| *e.borrow_mut() = CString::new(clean).unwrap());
41: }
42: 
43: /// UTF-8 description of the most recent failure ON THIS THREAD.
44: /// Valid until the next failing call from the same thread.
45: #[unsafe(no_mangle)]
46: pub extern "C" fn cortiq_last_error() -> *const c_char {
47:     LAST_ERROR.with(|e| e.borrow().as_ptr())
48: }
49: 
50: /// Engine version as a static UTF-8 string.
51: #[unsafe(no_mangle)]
52: pub extern "C" fn cortiq_version() -> *const c_char {
53:     static V: &str = concat!(env!("CARGO_PKG_VERSION"), "\0");
54:     V.as_ptr() as *const c_char
55: }
56: 
57: /// Open a `.cmf` file and build the pipeline. Returns an opaque handle,
58: /// or NULL (see `cortiq_last_error`). The file is memory-mapped: keep it
59: /// on storage for the handle's lifetime.
60: #[unsafe(no_mangle)]
61: pub extern "C" fn cortiq_load(path: *const c_char) -> *mut c_void {
62:     let result = catch_unwind(|| {
63:         if path.is_null() {
64:             set_error("path is NULL");
65:             return std::ptr::null_mut();
66:         }
67:         let path = match unsafe { CStr::from_ptr(path) }.to_str() {
68:             Ok(p) => p,
69:             Err(_) => {
70:                 set_error("path is not valid UTF-8");
71:                 return std::ptr::null_mut();
72:             }
73:         };
74:         let model = match CmfModel::open_sharded(path) {
75:             Ok(m) => Arc::new(m),
76:             Err(e) => {
77:                 set_error(&format!("open: {e}"));
78:                 return std::ptr::null_mut();
79:             }
80:         };
81:         let pipeline = match Pipeline::from_model(&model, SamplerConfig::default()) {
82:             Ok(p) => p,
83:             Err(e) => {
84:                 set_error(&format!("pipeline: {e}"));
85:                 return std::ptr::null_mut();
86:             }
87:         };
88:         Box::into_raw(Box::new(Ctx {
89:             cancel: pipeline.cancel.clone(),
90:             pipeline: Mutex::new(pipeline),
91:             enable_thinking: Mutex::new(None),
92:         })) as *mut c_void
93:     });
94:     result.unwrap_or_else(|_| {
95:         set_error("panic during load");
96:         std::ptr::null_mut()
97:     })
98: }
99: 
100: /// Globally enable or disable the discrete GPU (Vulkan/DX12/Metal) graph.
101: /// Must be called before `cortiq_load` to take effect.
102: #[unsafe(no_mangle)]
103: pub extern "C" fn cortiq_set_gpu(enable: bool) {
104:     cortiq_engine::pipeline::GLOBAL_USE_GPU.store(enable, std::sync::atomic::Ordering::Relaxed);
105: }
106: 
107: /// True when this build carries a working GPU backend AND the device
108: /// can bring an adapter up (Vulkan on Android, Metal on iOS/macOS).
109: /// Distinguishes "GPU off" from "GPU impossible": a CPU-only library
110: /// returns false here while `cortiq_set_gpu` still accepts the flag.
111: #[unsafe(no_mangle)]
112: pub extern "C" fn cortiq_gpu_available() -> bool {
113:     cortiq_engine::gpu::backend_available()
114: }
115: 
116: /// Pin the worker-pool size from the embedder instead of the
117: /// process-wide `CMF_THREADS` environment variable. 0 restores the
118: /// automatic choice (env, then big-core topology). Call before
119: /// `cortiq_load` — the pool is sized once per load.
120: #[unsafe(no_mangle)]
121: pub extern "C" fn cortiq_set_threads(n: i32) {
122:     cortiq_engine::pool::FORCED_THREADS
123:         .store(n.max(0) as usize, std::sync::atomic::Ordering::Relaxed);
124: }
125: 
126: /// Kernel thread ids of the current worker pool (Android/Linux) — what
127: /// ADPF's PerformanceHintManager needs to report work durations to the
128: /// scheduler. Copies up to `cap` ids into `out`, returns the total
129: /// worker count (call again with a larger buffer if it exceeds `cap`).
130: /// Returns 0 on platforms without stable kernel tids or before a load.
131: #[unsafe(no_mangle)]
132: pub extern "C" fn cortiq_worker_tids(out: *mut i32, cap: i32) -> i32 {
133:     let tids = match cortiq_engine::pool::WORKER_TIDS.lock() {
134:         Ok(t) => t.clone(),
135:         Err(_) => return 0,
136:     };
137:     if !out.is_null() && cap > 0 {
138:         let n = tids.len().min(cap as usize);
139:         unsafe { std::ptr::copy_nonoverlapping(tids.as_ptr(), out, n) };
140:     }
141:     tids.len() as i32
142: }
143: 
144: /// Cancel the generation currently running on this handle (safe from
145: /// any thread — this is the point: `cortiq_chat*` blocks its caller).
146: /// The engine checks the flag at every prefill chunk and decode step
147: /// and finishes with `finish_reason: "cancelled"`. No-op when nothing
148: /// runs; the flag clears itself once honoured.
149: #[unsafe(no_mangle)]
150: pub extern "C" fn cortiq_cancel(handle: *mut c_void) {
151:     if handle.is_null() {
152:         return;
153:     }
154:     let ctx = unsafe { &*(handle as *const Ctx) };
155:     ctx.cancel.store(true, std::sync::atomic::Ordering::Relaxed);
156: }
157: 
158: /// One-line execution summary as JSON, for status/About surfaces:
159: /// `{"simd":"neon","threads":4,"gpu_backend":true}`. `threads` is the
160: /// REAL worker-pool resolution (forced > CMF_THREADS > topology) —
161: /// the number the pool will actually spawn, valid before AND after
162: /// load. The returned pointer is a process-lifetime C string.
163: #[unsafe(no_mangle)]
164: pub extern "C" fn cortiq_execution_info() -> *const c_char {
165:     use std::sync::OnceLock;
166:     static INFO: OnceLock<std::ffi::CString> = OnceLock::new();
167:     INFO.get_or_init(|| {
168:         #[cfg(target_arch = "aarch64")]
169:         let simd = "neon";
170:         #[cfg(target_arch = "x86_64")]
171:         let simd = "avx2";
172:         #[cfg(not(any(target_arch = "aarch64", target_arch = "x86_64")))]
173:         let simd = "none";
174:         let threads = cortiq_engine::pool::Pool::effective_threads().max(1);
175:         let gpu = cortiq_engine::gpu::backend_available();
176:         std::ffi::CString::new(format!(
177:             "{{\"simd\":\"{simd}\",\"threads\":{threads},\"gpu_backend\":{gpu}}}"
178:         ))
179:         .expect("no interior NUL")
180:     })
181:     .as_ptr()
182: }
183: 
184: /// Release the handle. NULL is a no-op. Do not use the handle afterwards.
185: #[unsafe(no_mangle)]
186: pub extern "C" fn cortiq_free(handle: *mut c_void) {
187:     if handle.is_null() {
188:         return;
189:     }
190:     let _ = catch_unwind(AssertUnwindSafe(|| {
191:         drop(unsafe { Box::from_raw(handle as *mut Ctx) });
192:     }));
193: }
194: 
195: /// Streaming token callback: `token` is a NUL-terminated UTF-8 piece
196: /// (valid only during the call); return `true` to continue generating.
197: pub type CortiqTokenCb = Option<extern "C" fn(token: *const c_char, user: *mut c_void) -> bool>;
198: 
199: enum GenInput {
200:     Chat(String),
201:     Raw(String),
202:     History(Vec<(String, String)>),
203: }
204: 
205: fn run_generate(
206:     handle: *mut c_void,
207:     prompt: *const c_char,
208:     max_tokens: u32,
209:     chat: bool,
210:     cb: CortiqTokenCb,
211:     user: *mut c_void,
212: ) -> i32 {
213:     if handle.is_null() {
214:         set_error("handle is NULL");
215:         return -1;
216:     }
217:     if prompt.is_null() {
218:         set_error("prompt is NULL");
219:         return -1;
220:     }
221:     let prompt = match unsafe { CStr::from_ptr(prompt) }.to_str() {
222:         Ok(p) => p.to_string(),
223:         Err(_) => {
224:             set_error("prompt is not valid UTF-8");
225:             return -1;
226:         }
227:     };
228:     let input = if chat {
229:         GenInput::Chat(prompt)
230:     } else {
231:         GenInput::Raw(prompt)
232:     };
233:     run_generate_ids(handle, input, max_tokens, cb, user)
234: }
235: 
236: fn run_generate_ids(
237:     handle: *mut c_void,
238:     input: GenInput,
239:     max_tokens: u32,
240:     cb: CortiqTokenCb,
241:     user: *mut c_void,
242: ) -> i32 {
243:     let ctx = unsafe { &*(handle as *const Ctx) };
244:     let mut pipeline = match ctx.pipeline.lock() {
245:         Ok(g) => g,
246:         Err(_) => {
247:             set_error("pipeline mutex poisoned");
248:             return -1;
249:         }
250:     };
251:     // The raw pointer travels into the engine callback; the callback
252:     // contract (called synchronously on this thread) makes that sound.
253:     struct UserPtr(*mut c_void);
254:     unsafe impl Send for UserPtr {}
255:     impl UserPtr {
256:         // Accessor keeps the closure capturing &UserPtr — 2021 disjoint
257:         // capture would otherwise grab the raw pointer field itself.
258:         fn get(&self) -> *mut c_void {
259:             self.0
260:         }
261:     }
262:     let user = UserPtr(user);
263:     let on_token: Option<cortiq_engine::TokenCallback> = cb.map(|f| {
264:         Box::new(move |piece: &str| -> bool {
265:             match CString::new(piece.replace('\0', " ")) {
266:                 Ok(c) => f(c.as_ptr(), user.get()),
267:                 Err(_) => true,
268:             }
269:         }) as cortiq_engine::TokenCallback
270:     });
271:     let thinking = match ctx.enable_thinking.lock() {
272:         Ok(g) => *g,
273:         Err(_) => None,
274:     };
275:     let ids = match input {
276:         GenInput::Chat(prompt) => {
277:             let history = vec![("user".to_string(), prompt)];
278:             pipeline
279:                 .tokenizer
280:                 .apply_chat_template_opts(&history, thinking)
281:         }
282:         GenInput::Raw(prompt) => pipeline
283:             .tokenizer
284:             .with_bos(pipeline.tokenizer.encode(&prompt)),
285:         GenInput::History(history) => pipeline
286:             .tokenizer
287:             .apply_chat_template_opts(&history, thinking),
288:     };
289:     match pipeline.generate_from_ids(&ids, max_tokens as usize, None, on_token) {
290:         Ok(res) => res.tokens_generated as i32,
291:         Err(e) => {
292:             set_error(&format!("generate: {e}"));
293:             -1
294:         }
295:     }
296: }
297: 
298: /// Partial sampler options as JSON — absent fields keep their current
299: /// values. Accepted keys: temperature, top_p, top_k,
300: /// repetition_penalty, min_p, seed, greedy (true = argmax: temperature
301: /// pinned to 0), enable_thinking (false makes reasoning models —
302: /// Qwen3/3.5 — answer directly with no `<think>` block; true re-enables it;
303: /// absent/null keeps the current value). Applies to every subsequent generate
304: /// on this handle. Returns 0, or −1 (`cortiq_last_error`).
305: #[unsafe(no_mangle)]
306: pub extern "C" fn cortiq_set_options(handle: *mut c_void, options_json: *const c_char) -> i32 {
307:     catch_unwind(AssertUnwindSafe(|| {
308:         if handle.is_null() || options_json.is_null() {
309:             set_error("handle or options is NULL");
310:             return -1;
311:         }
312:         let json = match unsafe { CStr::from_ptr(options_json) }.to_str() {
313:             Ok(j) => j,
314:             Err(_) => {
315:                 set_error("options is not valid UTF-8");
316:                 return -1;
317:             }
318:         };
319:         #[derive(serde::Deserialize)]
320:         struct Opts {
321:             temperature: Option<f32>,
322:             top_p: Option<f32>,
323:             top_k: Option<u32>,
324:             repetition_penalty: Option<f32>,
325:             min_p: Option<f32>,
326:             seed: Option<u64>,
327:             greedy: Option<bool>,
328:             // Absent or `null` leaves the sticky value untouched (serde folds a
329:             // JSON `null` into the outer `None`); `true`/`false` pins it. To go
330:             // back to the template default, reload the handle.
331:             enable_thinking: Option<Option<bool>>,
332:         }
333:         let opts: Opts = match serde_json::from_str(json) {
334:             Ok(o) => o,
335:             Err(e) => {
336:                 set_error(&format!("options: {e}"));
337:                 return -1;
338:             }
339:         };
340:         let ctx = unsafe { &*(handle as *const Ctx) };
341:         let mut pipeline = match ctx.pipeline.lock() {
342:             Ok(g) => g,
343:             Err(_) => {
344:                 set_error("pipeline mutex poisoned");
345:                 return -1;
346:             }
347:         };
348:         let mut next = pipeline.sampler_config.clone();
349:         if let Some(v) = opts.temperature {
350:             if !v.is_finite() || v < 0.0 {
351:                 set_error("temperature must be finite and >= 0");
352:                 return -1;
353:             }
354:             next.temperature = v;
355:         }
356:         if let Some(v) = opts.top_p {
357:             if !v.is_finite() || !(0.0..=1.0).contains(&v) {
358:                 set_error("top_p must be finite and between 0 and 1");
359:                 return -1;
360:             }
361:             next.top_p = v;
362:         }
363:         if let Some(v) = opts.top_k {
364:             next.top_k = v;
365:         }
366:         if let Some(v) = opts.repetition_penalty {
367:             if !v.is_finite() || v <= 0.0 {
368:                 set_error("repetition_penalty must be finite and > 0");
369:                 return -1;
370:             }
371:             next.repetition_penalty = v;
372:         }
373:         if let Some(v) = opts.min_p {
374:             if !v.is_finite() || !(0.0..=1.0).contains(&v) {
375:                 set_error("min_p must be finite and between 0 and 1");
376:                 return -1;
377:             }
378:             next.min_p = v;
379:         }
380:         if opts.seed.is_some() {
381:             next.seed = opts.seed;
382:         }
383:         if opts.greedy == Some(true) {
384:             next.temperature = 0.0;
385:         }
386:         pipeline.set_sampler_config(next);
387:         drop(pipeline);
388:         if let Some(v) = opts.enable_thinking
389:             && let Ok(mut g) = ctx.enable_thinking.lock()
390:         {
391:             *g = v;
392:         }
393:         0
394:     }))
395:     .unwrap_or_else(|_| {
396:         set_error("panic during set_options");
397:         -1
398:     })
399: }
400: 
401: /// Multi-turn chat: `messages_json` is `[{"role": "...", "content":
402: /// "..."}, ...]` rendered through the file's own chat template — the
403: /// canonical way to carry a conversation (roles the template knows:
404: /// typically system / user / assistant). Same streaming/return contract
405: /// as `cortiq_chat`.
406: #[unsafe(no_mangle)]
407: pub extern "C" fn cortiq_chat_messages(
408:     handle: *mut c_void,
409:     messages_json: *const c_char,
410:     max_tokens: u32,
411:     cb: CortiqTokenCb,
412:     user: *mut c_void,
413: ) -> i32 {
414:     catch_unwind(AssertUnwindSafe(|| {
415:         if handle.is_null() || messages_json.is_null() {
416:             set_error("handle or messages is NULL");
417:             return -1;
418:         }
419:         let json = match unsafe { CStr::from_ptr(messages_json) }.to_str() {
420:             Ok(j) => j,
421:             Err(_) => {
422:                 set_error("messages is not valid UTF-8");
423:                 return -1;
424:             }
425:         };
426:         #[derive(serde::Deserialize)]
427:         struct Msg {
428:             role: String,
429:             content: String,
430:         }
431:         let msgs: Vec<Msg> = match serde_json::from_str(json) {
432:             Ok(m) => m,
433:             Err(e) => {
434:                 set_error(&format!("messages: {e}"));
435:                 return -1;
436:             }
437:         };
438:         if msgs.is_empty() {
439:             set_error("messages is empty");
440:             return -1;
441:         }
442:         let history: Vec<(String, String)> =
443:             msgs.into_iter().map(|m| (m.role, m.content)).collect();
444:         run_generate_ids(handle, GenInput::History(history), max_tokens, cb, user)
445:     }))
446:     .unwrap_or_else(|_| {
447:         set_error("panic during generate");
448:         -1
449:     })
450: }
451: 
452: /// One chat turn: the file's own chat template wraps the prompt (models
453: /// without a template fall back to plain completion). Tokens stream
454: /// through `cb`; returns the generated-token count, or −1
455: /// (`cortiq_last_error`).
456: #[unsafe(no_mangle)]
457: pub extern "C" fn cortiq_chat(
458:     handle: *mut c_void,
459:     prompt: *const c_char,
460:     max_tokens: u32,
461:     cb: CortiqTokenCb,
462:     user: *mut c_void,
463: ) -> i32 {
464:     catch_unwind(AssertUnwindSafe(|| {
465:         run_generate(handle, prompt, max_tokens, true, cb, user)
466:     }))
467:     .unwrap_or_else(|_| {
468:         set_error("panic during generate");
469:         -1
470:     })
471: }
472: 
473: /// Raw completion: the prompt goes to the model verbatim (plus the
474: /// tokenizer's BOS contract). Same streaming/return contract as
475: /// `cortiq_chat`.
476: #[unsafe(no_mangle)]
477: pub extern "C" fn cortiq_complete(
478:     handle: *mut c_void,
479:     prompt: *const c_char,
480:     max_tokens: u32,
481:     cb: CortiqTokenCb,
482:     user: *mut c_void,
483: ) -> i32 {
484:     catch_unwind(AssertUnwindSafe(|| {
485:         run_generate(handle, prompt, max_tokens, false, cb, user)
486:     }))
487:     .unwrap_or_else(|_| {
488:         set_error("panic during generate");
489:         -1
490:     })
491: }
492: 
493: /// Text → image (Lumina-Image 2.0 packed `.cmf`). Renders `prompt` at
494: /// `width`×`height` (multiples of 16) with `steps` denoising steps and
495: /// CFG `guidance` (≤1 disables CFG and halves the work — the right
496: /// default on phones), writing `height·width·3` interleaved RGB8 bytes
497: /// into caller-allocated `out_rgb`. `progress` (nullable) fires after
498: /// each denoising step with (step, total, user). The model file is
499: /// opened per call (mmap — cheap); weights stream from the map, so
500: /// peak RSS stays far below the file size. GPU (Metal / Vulkan via
501: /// `cortiq_set_gpu`) is probed against the CPU per process — enabling
502: /// it never makes generation slower. Returns 0 on success, -1 on
503: /// error (`cortiq_last_error` has the message).
504: #[unsafe(no_mangle)]
505: pub extern "C" fn cortiq_imagine(
506: 
507:     model_path: *const c_char,
508:     prompt: *const c_char,
509:     width: u32,
510:     height: u32,
511:     steps: u32,
512:     guidance: f32,
513:     seed: u64,
514:     out_rgb: *mut u8,
515:     progress: Option<extern "C" fn(step: u32, total: u32, user: *mut c_void) -> bool>,
516:     user: *mut c_void,
517: ) -> i32 {
518:     let res = catch_unwind(AssertUnwindSafe(|| {
519:         if model_path.is_null() || prompt.is_null() || out_rgb.is_null() {
520:             set_error("null argument");
521:             return -1;
522:         }
523:         let (path, prompt) = unsafe {
524:             let Ok(p) = CStr::from_ptr(model_path).to_str() else {
525:                 set_error("model_path is not UTF-8");
526:                 return -1;
527:             };
528:             let Ok(t) = CStr::from_ptr(prompt).to_str() else {
529:                 set_error("prompt is not UTF-8");
530:                 return -1;
531:             };
532:             (p.to_string(), t.to_string())
533:         };
534:         let params = cortiq_engine::imagegen::GenParams {
535:             height: height as usize,
536:             width: width as usize,
537:             steps: steps.max(1) as usize,
538:             guidance_scale: guidance,
539:             seed,
540:             ..Default::default()
541:         };
542:         let user_addr = user as usize; // callbacks may hop pool threads
543:         let img = match cortiq_engine::imagegen::generate(
544:             std::path::Path::new(&path),
545:             &prompt,
546:             &params,
547:             |i, n| {
548:                 if let Some(cb) = progress {
549:                     cb(i as u32, n as u32, user_addr as *mut c_void)
550:                 } else {
551:                     true
552:                 }
553:             },
554:         ) {
555:             Ok(v) => v,
556:             Err(e) => {
557:                 set_error(&e);
558:                 return -1;
559:             }
560:         };
561:         // [3, h, w] planar f32 in [0,1] → interleaved RGB8.
562:         let plane = (height as usize) * (width as usize);
563:         let dst = unsafe { std::slice::from_raw_parts_mut(out_rgb, plane * 3) };
564:         for p in 0..plane {
565:             for ch in 0..3 {
566:                 dst[p * 3 + ch] = (img[ch * plane + p].clamp(0.0, 1.0) * 255.0 + 0.5) as u8;
567:             }
568:         }
569:         0
570:     }));
571:     res.unwrap_or_else(|_| {
572:         set_error("GPU Out Of Memory or panic during image generation");
573:         -1
574:     })
575: }
576: 
577: 
578: #[cfg(test)]
579: mod tests {
580:     use super::*;
581: 
582:     /// The ABI functions are plain Rust calls in-crate: exercise the
583:     /// error paths without a model file.
584:     #[test]
585:     fn null_arguments_error_cleanly() {
586:         assert!(cortiq_load(std::ptr::null()).is_null());
587:         let err = unsafe { CStr::from_ptr(cortiq_last_error()) };
588:         assert!(!err.to_bytes().is_empty());
589:         assert_eq!(
590:             cortiq_chat(
591:                 std::ptr::null_mut(),
592:                 std::ptr::null(),
593:                 8,
594:                 None,
595:                 std::ptr::null_mut()
596:             ),
597:             -1
598:         );
599:         cortiq_free(std::ptr::null_mut());
600:         let v = unsafe { CStr::from_ptr(cortiq_version()) };
601:         assert!(v.to_str().unwrap().starts_with("0."));
602:     }
603: }
604: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-11T15:35:31-07:00
Completed At: 2026-08-11T15:35:37-07:00

				The command exited with code 0.
				Output:
				<truncated 1 lines>
      |         ^^^^^^^^ help: if this is intentional, prefix it with an underscore: `_ape_slot`

warning: unused variable: `kv`
     --> crates\cortiq-engine\src\gpu_wgpu.rs:28774:9
      |
28774 |     let kv = frame_buf(c, 105, hd * 4, false);
      |         ^^ help: if this is intentional, prefix it with an underscore: `_kv`

warning: unused variable: `state2`
     --> crates\cortiq-engine\src\gpu_wgpu.rs:30236:13
      |
30236 |         let state2 = frame_buf(c, 46, h.hc * g.hidden * 4, true);
      |             ^^^^^^ help: if this is intentional, prefix it with an underscore: `_state2`

warning: unnecessary `unsafe` block
    --> crates\cortiq-engine\src\qtensor.rs:3930:5
     |
3930 |     unsafe {
     |     ^^^^^^ unnecessary `unsafe` block
     |
     = note: `#[warn(unused_unsafe)]` (part of `#[warn(unused)]`) on by default

warning: unnecessary `unsafe` block
    --> crates\cortiq-engine\src\qtensor.rs:8100:5
     |
8100 |     unsafe {
     |     ^^^^^^ unnecessary `unsafe` block

warning: variable does not need to be mutable
   --> crates\cortiq-engine\src\vae3d.rs:143:24
    |
143 |     let (mut overlaps, mut remaining);
    |                        ----^^^^^^^^^
    |                        |
    |                        help: remove this `mut`

warning: method `gpu_block` is never used
   --> crates\cortiq-engine\src\dit.rs:668:8
    |
329 | impl NextDit {
    | ------------ method in this implementation
...
668 |     fn gpu_block(
    |        ^^^^^^^^^
    |
    = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

warning: function `last_grew` is never used
    --> crates\cortiq-engine\src\dsv4.rs:3568:4
     |
3568 | fn last_grew(now: u64) -> u64 {
     |    ^^^^^^^^^

warning: function `compressed_written` is never used
    --> crates\cortiq-engine\src\dsv4.rs:3589:4
     |
3589 | fn compressed_written(kv_id: u64, li: usize) -> usize {
     |    ^^^^^^^^^^^^^^^^^^

warning: function `host_tail_walk` is never used
    --> crates\cortiq-engine\src\dsv4.rs:4458:4
     |
4458 | fn host_tail_walk(
     |    ^^^^^^^^^^^^^^

warning: function `fp_f32` is never used
    --> crates\cortiq-engine\src\gpu.rs:1695:15
     |
1695 | pub(crate) fn fp_f32(data: &[f32]) -> u64 {
     |               ^^^^^^

warning: fields `silu_down`, `gdn_step_k`, and `layout_silu_down` are never read
    --> crates\cortiq-engine\src\gpu_wgpu.rs:9383:5
     |
9291 | struct Ctx {
     |        --- fields in this struct
...
9383 |     silu_down: wgpu::ComputePipeline,
     |     ^^^^^^^^^
...
9446 |     gdn_step_k: wgpu::ComputePipeline,
     |     ^^^^^^^^^^
...
9480 |     layout_silu_down: wgpu::BindGroupLayout,
     |     ^^^^^^^^^^^^^^^^

warning: field `dpar` is never read
    --> crates\cortiq-engine\src\gpu_wgpu.rs:9646:5
     |
9626 | struct Scratch {
     |        ------- field in this struct
...
9646 |     dpar: Option<wgpu::Buffer>,
     |     ^^^^

warning: fields `kv_u`, `at_u`, and `rope_u` are never read
    --> crates\cortiq-engine\src\gpu_wgpu.rs:9714:5
     |
9680 | struct GraphScratch {
     |        ------------ fields in this struct
...
9714 |     kv_u: Option<wgpu::Buffer>,   // 16 bytes: [nkv, hd, cap, position]
     |     ^^^^
9715 |     at_u: Option<wgpu::Buffer>,   // 32 bytes: [nh, nh/nkv, hd, cap, pos+1, 0, 0, 0]
     |     ^^^^
9716 |     rope_u: Option<wgpu::Buffer>, // 32 bytes: [nh, nkv, hd, rd, pos, flags, eps, 0]
     |     ^^^^^^

warning: associated function `ensure_uniform` is never used
    --> crates\cortiq-engine\src\gpu_wgpu.rs:9754:8
     |
9730 | impl GraphScratch {
     | ----------------- associated function in this implementation
...
9754 |     fn ensure_uniform(
     |        ^^^^^^^^^^^^^^

warning: function `bind_buf_off` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:18221:4
      |
18221 | fn bind_buf_off(binding: u32, buf: &wgpu::Buffer, off: u64, size: u64) -> wgpu::BindGroupEntry<'_> {
      |    ^^^^^^^^^^^^

warning: function `encode_f32matvec_k` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:18649:4
      |
18649 | fn encode_f32matvec_k(
      |    ^^^^^^^^^^^^^^^^^^

warning: function `encode_f32matvec_k_p` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:18750:4
      |
18750 | fn encode_f32matvec_k_p(
      |    ^^^^^^^^^^^^^^^^^^^^

warning: function `encode_f32matvec_off` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:18830:4
      |
18830 | fn encode_f32matvec_off(
      |    ^^^^^^^^^^^^^^^^^^^^

warning: function `encode_silu_down` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:19237:4
      |
19237 | fn encode_silu_down(
      |    ^^^^^^^^^^^^^^^^

warning: function `encode_hc_fold_k` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:21992:4
      |
21992 | fn encode_hc_fold_k(
      |    ^^^^^^^^^^^^^^^^

warning: function `encode_hc_expand_k` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:22090:4
      |
22090 | fn encode_hc_expand_k(
      |    ^^^^^^^^^^^^^^^^^^

warning: function `encode_moe_chain` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:22293:4
      |
22293 | fn encode_moe_chain(
      |    ^^^^^^^^^^^^^^^^

warning: field `batch` is never read
     --> crates\cortiq-engine\src\gpu_wgpu.rs:24663:5
      |
24661 | pub struct Dsv4SpecShadow {
      |            -------------- field in this struct
24662 |     kv_id: u64,
24663 |     batch: usize,
      |     ^^^^^

warning: function `encode_axpy` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:28401:4
      |
28401 | fn encode_axpy(
      |    ^^^^^^^^^^^

warning: function `encode_axpy_p` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:28415:4
      |
28415 | fn encode_axpy_p(
      |    ^^^^^^^^^^^^^

warning: function `encode_kv_pool` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:28478:4
      |
28478 | fn encode_kv_pool(
      |    ^^^^^^^^^^^^^^

warning: function `encode_fill_zero` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:29001:4
      |
29001 | fn encode_fill_zero(
      |    ^^^^^^^^^^^^^^^^

warning: function `encode_fill_zero_p` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:29013:4
      |
29013 | fn encode_fill_zero_p(
      |    ^^^^^^^^^^^^^^^^^^

warning: function `encode_index_scores` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:29034:4
      |
29034 | fn encode_index_scores(
      |    ^^^^^^^^^^^^^^^^^^^

warning: function `encode_top_k` is never used
     --> crates\cortiq-engine\src\gpu_wgpu.rs:29085:4
      |
29085 | fn encode_top_k(
      |    ^^^^^^^^^^^^

warning: field `cmd_pool` is never read
  --> crates\cortiq-engine\src\vulkan.rs:49:5
   |
43 | pub struct Ctx {
   |            --- field in this struct
...
49 |     cmd_pool: vk::CommandPool,
   |     ^^^^^^^^

warning: methods `f32_parts`, `q1_parts`, and `q8_row_parts` are never used
   --> crates\cortiq-engine\src\qtensor.rs:359:19
    |
168 | impl QTensor {
    | ------------ methods in this implementation
...
359 |     pub(crate) fn f32_parts(&self) -> Option<(&[f32], usize, usize)> {
    |                   ^^^^^^^^^
...
372 |     pub(crate) fn q1_parts(&self) -> Option<(usize, usize, usize)> {
    |                   ^^^^^^^^
...
436 |     pub(crate) fn q8_row_parts(&self) -> Option<(usize, usize, usize, &[f32])> {
    |                   ^^^^^^^^^^^^

warning: constant `SIGN5_I8` is never used
    --> crates\cortiq-engine\src\qtensor.rs:6038:7
     |
6038 | const SIGN5_I8: [[i8; 5]; 256] = {
     |       ^^^^^^^^

warning: function `num_cpus` is never used
   --> crates\cortiq-engine\src\runtime.rs:308:4
    |
308 | fn num_cpus() -> usize {
    |    ^^^^^^^^

warning: method `chatml_fallback` is never used
   --> crates\cortiq-engine\src\tokenizer.rs:997:8
    |
186 | impl Tokenizer {
    | -------------- method in this implementation
...
997 |     fn chatml_fallback(&self, messages: &[(String, String)]) -> Vec<u32> {
    |        ^^^^^^^^^^^^^^^

warning: `cortiq-engine` (lib) generated 64 warnings (run `cargo fix --lib -p cortiq-engine` to apply 30 suggestions)
    Finished `release` profile [optimized] target(s) in 0.77s

Created At: 2026-08-11T15:35:38-07:00
Completed At: 2026-08-11T15:35:38-07:00
Found 6 results
cortiq_ffi.dll
cortiq_ffi.dll.exp
cortiq_ffi.dll.lib
deps/cortiq_ffi.dll
deps/cortiq_ffi.dll.exp
deps/cortiq_ffi.dll.lib

Created At: 2026-08-11T15:35:39-07:00
Tool is running as a background task with task id: 2237c28f-cf74-4d36-b556-809a825fc7ea/task-23
Task Description: Copy-Item -Force "p:\Downloaded\ComfyUI_windows_portable\ComfyUI\cmf_source\target\release\cortiq_ffi.dll" "p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\bin\cortiq_ffi.dll"
Task logs are available at: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-23.log

Created At: 2026-08-11T15:35:45-07:00
Completed At: 2026-08-11T15:35:45-07:00
Task: 2237c28f-cf74-4d36-b556-809a825fc7ea/task-23
Status: RUNNING
Log: C:\Users\blibd\.gemini\antigravity\brain\2237c28f-cf74-4d36-b556-809a825fc7ea\.system_generated\tasks\task-23.log
Last progress: never


REMINDER: Do not call this tool again to poll or wait for updates. You will be automatically notified when the task completes or a message arrives. If you need a bounded wait, use the `schedule` tool -- it waits silently in the background and suppresses its notification if you are woken by another event.

Created At: 2026-08-11T15:35:47-07:00
Completed At: 2026-08-11T15:35:47-07:00
Found 2 results
cortiq_ffi.dll
cortiq_ffi.dll.lib

Created At: 2026-08-11T15:35:47-07:00
Tool is running as a background task with task id: 2237c28f-cf74-4d36-b556-809a825fc7ea/task-29
Task Description: Get-Item "p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\bin\cortiq_ffi.dll", "p:\Downloaded\ComfyUI_windows_portable\ComfyUI\cmf_source\target\release\cortiq_ffi.dll" | Select-Object FullName, Length, LastWriteTime
Task logs are available at: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-29.log

Created At: 2026-08-11T15:35:53-07:00
Completed At: 2026-08-11T15:35:54-07:00
File Path: `file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-29.log`
Total Lines: 1
Total Bytes: 0
Showing lines 1 to 1
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: 
The above content shows the entire, complete file contents of the requested file.

The following is a <SYSTEM_MESSAGE> not actually sent by the user. It is provided by the system as important information to pay attention to.

<SYSTEM_MESSAGE>
[Message] timestamp=2026-08-11T22:35:53Z sender=2237c28f-cf74-4d36-b556-809a825fc7ea/task-23 priority=MESSAGE_PRIORITY_HIGH content=Task id "2237c28f-cf74-4d36-b556-809a825fc7ea/task-23" finished with result:

				The command exited with code 0.
				Output:
				Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.


Log: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-23.log
</SYSTEM_MESSAGE>

Created At: 2026-08-11T15:35:54-07:00
Completed At: 2026-08-11T15:35:54-07:00
File Path: `file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-29.log`
Total Lines: 1
Total Bytes: 0
Showing lines 1 to 1
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-11T15:35:57-07:00
Tool is running as a background task with task id: 2237c28f-cf74-4d36-b556-809a825fc7ea/task-36
Task Description: python -c "import sys; sys.path.insert(0, r'p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF'); from wrapper import CMFWrapper; wrapper = CMFWrapper(); print('Has cortiq_imagine:', hasattr(wrapper.lib, 'cortiq_imagine')); print('Execution info:', wrapper.get_execution_info())"
Task logs are available at: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-36.log

The following is a <SYSTEM_MESSAGE> not actually sent by the user. It is provided by the system as important information to pay attention to.

<SYSTEM_MESSAGE>
[Message] timestamp=2026-08-11T22:35:58Z sender=2237c28f-cf74-4d36-b556-809a825fc7ea/task-29 priority=MESSAGE_PRIORITY_HIGH content=Task id "2237c28f-cf74-4d36-b556-809a825fc7ea/task-29" finished with result:

				The command exited with code 0.
				Output:
				Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.

FullName                                                                                   Length LastWriteTime
--------                                                                                   ------ -------------
P:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF\bin\cortiq_ffi.dll 13671424 8/11/2026 3:33:48 PM
P:\Downloaded\ComfyUI_windows_portable\ComfyUI\cmf_source\target\release\cortiq_ffi.dll  13671424 8/11/2026 3:33:48 PM



Log: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-29.log
</SYSTEM_MESSAGE>

Created At: 2026-08-11T15:36:03-07:00
Completed At: 2026-08-11T15:36:03-07:00
File Path: `file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-36.log`
Total Lines: 2
Total Bytes: 127
Showing lines 1 to 2
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.
2: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-11T15:36:04-07:00
Tool is running as a background task with task id: 2237c28f-cf74-4d36-b556-809a825fc7ea/task-41
Task Description: p:\Downloaded\ComfyUI_windows_portable\python_embeded\python.exe -c "import sys; sys.path.insert(0, r'p:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF'); from wrapper import CMFWrapper; wrapper = CMFWrapper(); print('Has cortiq_imagine:', hasattr(wrapper.lib, 'cortiq_imagine')); print('Execution info:', wrapper.get_execution_info())"
Task logs are available at: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-41.log

Created At: 2026-08-11T15:36:10-07:00
Completed At: 2026-08-11T15:36:10-07:00
File Path: `file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-41.log`
Total Lines: 1
Total Bytes: 0
Showing lines 1 to 1
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-11T15:36:10-07:00
Completed At: 2026-08-11T15:36:11-07:00
Task: 2237c28f-cf74-4d36-b556-809a825fc7ea/task-41
Status: RUNNING
Log: C:\Users\blibd\.gemini\antigravity\brain\2237c28f-cf74-4d36-b556-809a825fc7ea\.system_generated\tasks\task-41.log
Last progress: never


REMINDER: Do not call this tool again to poll or wait for updates. You will be automatically notified when the task completes or a message arrives. If you need a bounded wait, use the `schedule` tool -- it waits silently in the background and suppresses its notification if you are woken by another event.

Created At: 2026-08-11T15:36:13-07:00
Completed At: 2026-08-11T15:36:13-07:00
Message sent to "b8888b03-2e45-47f5-96ec-b7096fc06bc6".

The following is a <SYSTEM_MESSAGE> not actually sent by the user. It is provided by the system as important information to pay attention to.

<SYSTEM_MESSAGE>
[Message] timestamp=2026-08-11T22:36:11Z sender=2237c28f-cf74-4d36-b556-809a825fc7ea/task-36 priority=MESSAGE_PRIORITY_HIGH content=Task id "2237c28f-cf74-4d36-b556-809a825fc7ea/task-36" finished with result:

				The command exited with code 0.
				Output:
				Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.
Has cortiq_imagine: True
Execution info: {"simd":"avx2","threads":7,"gpu_backend":true}


Log: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-36.log
</SYSTEM_MESSAGE>

### Summary of Completed Work

- **Built `cortiq-ffi` in Release GPU Mode**: Executed `cargo build -p cortiq-ffi --release --features gpu` in `cmf_source`. Built successfully.
- **Copied Dynamic Library**: Copied `cortiq_ffi.dll` to `custom_nodes\Comfy-CMF\bin\cortiq_ffi.dll`.
- **Verified C-FFI Integration in `wrapper.py`**:
  - Bound `cortiq_imagine` in `CMFWrapper._bind_signatures()` matching C ABI signatures.
  - Verified `generate_image` method in `CMFWrapper` which allocates `(height, width, 3)` uint8 NumPy memory, calls `cortiq_imagine`, and returns a normalized `[1, height, width, 3]` `float32` PyTorch tensor.
  - Verified execution with `Execution info: {"simd":"avx2","threads":7,"gpu_backend":true}` and `Has cortiq_imagine: True`.

The following is a <SYSTEM_MESSAGE> not actually sent by the user. It is provided by the system as important information to pay attention to.

<SYSTEM_MESSAGE>
[Message] timestamp=2026-08-11T22:36:25Z sender=2237c28f-cf74-4d36-b556-809a825fc7ea/task-41 priority=MESSAGE_PRIORITY_HIGH content=Task id "2237c28f-cf74-4d36-b556-809a825fc7ea/task-41" finished with result:

				The command exited with code 0.
				Output:
				Type '. al' to load alias definitions, or '. lp' to load entire profile. '. lc' to load chocolatey and '. lco' to load conda.
Has cortiq_imagine: True
Execution info: {"simd":"avx2","threads":7,"gpu_backend":true}


Log: file:///C:/Users/blibd/.gemini/antigravity/brain/2237c28f-cf74-4d36-b556-809a825fc7ea/.system_generated/tasks/task-41.log
</SYSTEM_MESSAGE>

The portable Python runtime background test task also finished successfully with code 0:
- `Has cortiq_imagine`: `True`
- `Execution info`: `{"simd":"avx2","threads":7,"gpu_backend":true}`

All tasks are complete.

---
