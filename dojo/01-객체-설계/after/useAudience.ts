import { useState } from 'react';

export interface Audience {
  amount: number;
  hasInvitation: boolean;
  hasTicket: boolean;
}

export const useAudience = ({ amount, hasInvitation, hasTicket }: Audience) => {
  const [audience, setAudience] = useState({
    amount,
    hasInvitation,
    hasTicket,
  });

  const handleAudience = (audience: Audience) => setAudience(audience);

  return {
    audience,
    setAudience,
    handleAudience,
  };
};
