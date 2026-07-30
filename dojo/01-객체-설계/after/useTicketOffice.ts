import { useState } from 'react';
import { TICKET_FEE } from '.';

export const useTicketOffice = (tickets: number, amount: number) => {
  const [ticketOffice, setTicketOffice] = useState({
    tickets,
    amount,
  });

  // ticketOffice가 audience에 의존한다 (hasInvitation)
  const handleTicketOffice = (hasInvitation: boolean) =>
    setTicketOffice((prev) => ({
      ...prev,
      tickets: prev.tickets - 1,
      amount: prev.amount + (hasInvitation ? 0 : TICKET_FEE),
    }));

  return {
    ticketOffice,
    handleTicketOffice,
  };
};
