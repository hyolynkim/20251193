# 20251193
import React, { useState } from 'react';
import { Play, RotateCcw, ChevronRight, ChevronLeft } from 'lucide-react';

const App = () => {
  const [step, setStep] = useState(0);

  // 스택 시나리오 정의
  const scenario = [
    { code: '// 스택 선언\nstd::stack<std::string> s;', stack: [], action: '시작' },
    { code: 's.push("🌸 벚꽃");', stack: ["🌸 벚꽃"], action: 'PUSH' },
    { code: 's.push("📝 중간고사");', stack: ["🌸 벚꽃", "📝 중간고사"], action: 'PUSH' },
    { code: 's.push("🍵 말차");', stack: ["🌸 벚꽃", "📝 중간고사", "🍵 말차"], action: 'PUSH' },
    { code: '// 현재 TOP 확인: "🍵 말차"\ns.top();', stack: ["🌸 벚꽃", "📝 중간고사", "🍵 말차"], action: 'TOP', highlight: true },
    { code: 's.pop(); // 말차 제거', stack: ["🌸 벚꽃", "📝 중간고사"], action: 'POP' },
    { code: 's.push("☕ 커피");', stack: ["🌸 벚꽃", "📝 중간고사", "☕ 커피"], action: 'PUSH' },
    { code: 's.push("🍪 두쫀쿠");', stack: ["🌸 벚꽃", "📝 중간고사", "☕ 커피", "🍪 두쫀쿠"], action: 'PUSH' },
    { code: 's.push("🧈 버터떡");', stack: ["🌸 벚꽃", "📝 중간고사", "☕ 커피", "🍪 두쫀쿠", "🧈 버터떡"], action: 'PUSH' },
    { code: 's.push("🍰 케이크");', stack: ["🌸 벚꽃", "📝 중간고사", "☕ 커피", "🍪 두쫀쿠", "🧈 버터떡", "🍰 케이크"], action: 'PUSH' },
    { code: 's.push("📖 공부");', stack: ["🌸 벚꽃", "📝 중간고사", "☕ 커피", "🍪 두쫀쿠", "🧈 버터떡", "🍰 케이크", "📖 공부"], action: 'PUSH' },
    { code: 's.push("💕 분홍색");', stack: ["🌸 벚꽃", "📝 중간고사", "☕ 커피", "🍪 두쫀쿠", "🧈 버터떡", "🍰 케이크", "📖 공부", "💕 분홍색"], action: 'PUSH' },
    { code: '// 최종 상태 확인\ns.size(); // 8', stack: ["🌸 벚꽃", "📝 중간고사", "☕ 커피", "🍪 두쫀쿠", "🧈 버터떡", "🍰 케이크", "📖 공부", "💕 분홍색"], action: '완료' },
  ];

  const nextStep = () => setStep((s) => Math.min(s + 1, scenario.length - 1));
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));
  const reset = () => setStep(0);

  const current = scenario[step];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4 font-sans text-gray-800">
      <div className="max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200">
        {/* 헤더 */}
        <div className="bg-blue-500 p-6 text-white text-center">
          <h1 className="text-2xl font-bold">🌸 벚꽃 학기 스택 시뮬레이터</h1>
          <p className="text-blue-100 mt-1">객체 기반 스택 연산 시각화</p>
        </div>

        {/* 메인 컨텐츠 (이미지 스타일 레이아웃) */}
        <div className="flex flex-col md:flex-row min-h-[400px]">
          {/* 왼쪽: 코드 영역 */}
          <div className="flex-1 p-8 flex items-center justify-center border-b md:border-b-0 md:border-r border-blue-100 bg-gray-50">
            <div className="w-full">
               <div className="text-sm font-mono text-blue-400 mb-2">// Current Operation</div>
               <div className="bg-white p-6 rounded-lg border-2 border-blue-300 shadow-sm min-h-[120px] flex items-center">
                  <pre className="text-xl md:text-2xl font-bold text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {current.code}
                  </pre>
               </div>
               <div className="mt-4 flex gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    current.action === 'PUSH' ? 'bg-green-100 text-green-700' :
                    current.action === 'POP' ? 'bg-red-100 text-red-700' :
                    current.action === 'TOP' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {current.action}
                  </span>
                  <span className="text-xs text-gray-400 self-center">Step {step} / {scenario.length - 1}</span>
               </div>
            </div>
          </div>

          {/* 오른쪽: 스택 비주얼 영역 */}
          <div className="flex-1 p-8 flex flex-col items-center justify-end bg-white relative">
            <div className="w-full max-w-[280px] flex flex-col-reverse border-b-4 border-gray-400">
              {/* 스택 바닥 가이드 */}
              <div className="absolute bottom-4 text-xs text-gray-300 font-bold uppercase tracking-widest">Stack Base</div>
              
              {/* 실제 스택 아이템 */}
              {current.stack.map((item, idx) => (
                <div 
                  key={idx}
                  className={`
                    h-14 mb-1 flex items-center justify-center border-2 border-gray-800 text-xl font-bold transition-all duration-300 transform
                    ${idx === current.stack.length - 1 && current.highlight ? 'bg-yellow-100 border-yellow-500 scale-105' : 'bg-white'}
                    ${idx === current.stack.length - 1 ? 'border-b-4' : 'border-b-2'}
                  `}
                  style={{
                    animation: 'slideIn 0.3s ease-out'
                  }}
                >
                  {item}
                  {idx === current.stack.length - 1 && (
                    <span className="absolute -right-12 text-xs font-bold text-red-500">TOP</span>
                  )}
                </div>
              ))}
              
              {current.stack.length === 0 && (
                <div className="h-14 flex items-center justify-center text-gray-300 italic">
                  Stack is Empty
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 하단 컨트롤 바 */}
        <div className="bg-gray-100 p-4 flex justify-between items-center border-t border-gray-200">
          <button 
            onClick={reset}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors text-gray-600"
            title="초기화"
          >
            <RotateCcw size={24} />
          </button>
          
          <div className="flex gap-4">
            <button 
              onClick={prevStep}
              disabled={step === 0}
              className="flex items-center gap-2 px-6 py-2 bg-white border border-gray-300 rounded-lg font-bold hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <ChevronLeft size={20} /> 이전
            </button>
            <button 
              onClick={nextStep}
              disabled={step === scenario.length - 1}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md transition-all"
            >
              다음 <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes slideIn {
          from { transform: translateY(-20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}} />

      <div className="mt-8 text-center text-gray-400 text-sm">
        <p>AI융합학부 데이터구조 - 스택 시나리오 실습</p>
        <p className="mt-1">제한 조건: 크기 10 이하 유지 (현재 최대 8)</p>
      </div>
    </div>
  );
};

export default App;
