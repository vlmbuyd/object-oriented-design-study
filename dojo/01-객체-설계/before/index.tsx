import { useState } from 'react';

export default function Theater() {
  // 🚨 문제점 1: 소극장이 매표소(TicketOffice)의 데이터 상태를 직접 가지고 있습니다.
  const [ticketOffice, setTicketOffice] = useState({
    tickets: 10,
    amount: 0,
  });

  // 🚨 문제점 2: 소극장이 관람객(Audience)의 가방(Bag) 데이터 상태를 직접 가지고 있습니다.
  const [audience1, setAudience1] = useState({
    amount: 20000,
    hasInvitation: false,
    hasTicket: false,
  });

  const [audience2, setAudience2] = useState({
    amount: 5000,
    hasInvitation: true,
    hasTicket: false,
  });

  const TICKET_FEE = 10000;

  // 🚨 문제점 3: 소극장(Theater)이 관람객의 가방을 열어보고, 매표소의 돈을 직접 계산합니다. (절차적 프로그래밍)
  const handleEnter = (audience, setAudience) => {
    // 소극장이 관람객의 초대장 여부를 직접 확인합니다.
    if (audience.hasInvitation) {
      setTicketOffice((prev) => ({
        ...prev,
        tickets: prev.tickets - 1,
      }));
      setAudience({
        ...audience,
        hasInvitation: false,
        hasTicket: true,
      });
    } else {
      // 소극장이 관람객의 현금을 직접 확인하고 차감합니다.
      if (audience.amount >= TICKET_FEE) {
        setAudience({
          ...audience,
          amount: audience.amount - TICKET_FEE,
          hasTicket: true,
        });

        // 소극장이 매표소의 현금을 직접 증가시킵니다.
        setTicketOffice((prev) => ({
          ...prev,
          tickets: prev.tickets - 1,
          amount: prev.amount + TICKET_FEE,
        }));
      } else {
        alert('현금이 부족합니다.');
      }
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>🎬 오브젝트 소극장 (실습용 초기 코드)</h2>

      <div
        style={{
          border: '1px solid #ccc',
          padding: '10px',
          marginBottom: '20px',
        }}
      >
        <h3>매표소 (TicketOffice)</h3>
        <p>남은 티켓: {ticketOffice.tickets}장</p>
        <p>보유 현금: {ticketOffice.amount}원</p>
      </div>

      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ border: '1px solid #ccc', padding: '10px' }}>
          <h3>관람객 1 (초대장 X)</h3>
          <p>보유 현금: {audience1.amount}원</p>
          <p>티켓 유무: {audience1.hasTicket ? '✅ 있음' : '❌ 없음'}</p>
          <button onClick={() => handleEnter(audience1, setAudience1)}>
            소극장 입장
          </button>
        </div>

        <div style={{ border: '1px solid #ccc', padding: '10px' }}>
          <h3>관람객 2 (초대장 O)</h3>
          <p>보유 현금: {audience2.amount}원</p>
          <p>초대장 유무: {audience2.hasInvitation ? '✅ 있음' : '❌ 없음'}</p>
          <p>티켓 유무: {audience2.hasTicket ? '✅ 있음' : '❌ 없음'}</p>
          <button onClick={() => handleEnter(audience2, setAudience2)}>
            소극장 입장
          </button>
        </div>
      </div>
    </div>
  );
}
