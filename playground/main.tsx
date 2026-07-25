import React from "react";
import { createRoot } from "react-dom/client";

// ── 실습할 컴포넌트를 여기서 바꿔 끼운다 ────────────────────────────────
// 지금 작업 중인 dojo 파일을 import 해서 아래 Current 에 연결하세요.
//   예) import Current from "../dojo/chapter_1/Theater";
//   예) import Current from "../dojo/07/after";
//
// 아직 연결 전이면 아래 안내 화면이 뜹니다.

const Placeholder = () => (
  <div style={{ fontFamily: "sans-serif", padding: 24, lineHeight: 1.6 }}>
    <h1>🥋 오브젝트 dojo 플레이그라운드</h1>
    <p>
      <code>playground/main.tsx</code> 상단에서 지금 실습 중인 dojo 컴포넌트를
      <code> import </code> 해 <code>Current</code> 에 연결하세요.
    </p>
    <p style={{ color: "#666" }}>
      저장하면 화면이 자동으로 갱신됩니다(HMR).
    </p>
  </div>
);

const Current = Placeholder;

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Current />
  </React.StrictMode>,
);
