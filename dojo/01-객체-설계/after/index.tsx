import { Audience, useAudience } from './useAudience';
import { useTicketOffice } from './useTicketOffice';

export const TICKET_FEE = 10000;

export default function Theater() {
  const { ticketOffice, handleTicketOffice } = useTicketOffice(10, 0);

  const { audience: audience1, handleAudience: handleAudience1 } = useAudience({
    amount: 20000,
    hasInvitation: false,
    hasTicket: false,
  });

  const { audience: audience2, handleAudience: handleAudience2 } = useAudience({
    amount: 5000,
    hasInvitation: true,
    hasTicket: false,
  });

  const handleEnter = (audience: Audience) => {
    const hasInvitation = audience.hasInvitation;

    if (hasInvitation) {
      handleTicketOffice(hasInvitation);
      handleAudience1({
        ...audience,
        hasInvitation: false,
        hasTicket: true,
      });
    } else {
      if (audience.amount >= TICKET_FEE) {
        handleTicketOffice(hasInvitation);
        handleAudience2({
          ...audience,
          amount: audience.amount - TICKET_FEE,
          hasTicket: true,
        });
      } else {
        alert('현금이 부족합니다.');
      }
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>🎬 오브젝트 소극장</h2>

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
          <button onClick={() => handleEnter(audience1)}>소극장 입장</button>
        </div>

        <div style={{ border: '1px solid #ccc', padding: '10px' }}>
          <h3>관람객 2 (초대장 O)</h3>
          <p>보유 현금: {audience2.amount}원</p>
          <p>초대장 유무: {audience2.hasInvitation ? '✅ 있음' : '❌ 없음'}</p>
          <p>티켓 유무: {audience2.hasTicket ? '✅ 있음' : '❌ 없음'}</p>
          <button onClick={() => handleEnter(audience2)}>소극장 입장</button>
        </div>
      </div>
    </div>
  );
}
