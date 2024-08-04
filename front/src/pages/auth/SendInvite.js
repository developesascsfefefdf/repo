import React, { useState } from 'react';
import { Button, TextField, Typography } from '@mui/material';
import { useSendInviteLinkMutation } from '../../services/userAuthApi';

const SendInvite = () => {
  const [email, setEmail] = useState('');
  const [sendInviteLink, { isLoading, isSuccess, isError, error }] = useSendInviteLinkMutation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    await sendInviteLink({ email });
  };

  return (
    <div>
      <Typography variant="h4">Send Invite Link</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          fullWidth
        />
        <Button type="submit" variant="contained" color="primary" disabled={isLoading}>
          Send Invite
        </Button>
      </form>
      {isSuccess && <Typography>Invite link sent successfully!</Typography>}
      {isError && <Typography color="error">{error.data.error}</Typography>}
    </div>
  );
};

export default SendInvite;
