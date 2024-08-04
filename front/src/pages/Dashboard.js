import React, { useEffect, useState } from 'react';
import { Button, CssBaseline, Grid, Typography, Table, TableBody, TableCell, TableHead, TableRow, IconButton, TextField } from '@mui/material';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { unSetUserToken } from '../features/authSlice';
import { getToken, removeToken } from '../services/LocalStorageService';
import ChangePassword from './auth/ChangePassword';
import { useGetLoggedUserQuery, useGetAllUsersQuery, useUpdateUserMutation, useDeleteUserMutation } from '../services/userAuthApi';
import { setUserInfo, unsetUserInfo } from '../features/userSlice';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SendInvite from './auth/SendInvite';

const Dashboard = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { access_token } = getToken();
  const { data: userData, isSuccess: userIsSuccess, isError: userIsError, error: userError } = useGetLoggedUserQuery(access_token);
  const { data: usersData, isSuccess: usersIsSuccess, isError: usersIsError, error: usersError, refetch: refetchUsers } = useGetAllUsersQuery(access_token);
  const [updateUser] = useUpdateUserMutation();
  const [deleteUser] = useDeleteUserMutation();

  const handleLogout = () => {
    dispatch(unsetUserInfo({ name: "", email: "" }));
    dispatch(unSetUserToken({ access_token: null }));
    removeToken();
    navigate('/login');
  };

  useEffect(() => {
    if (userData && userIsSuccess) {
      console.log('Logged in user data:', userData);
      dispatch(setUserInfo({
        email: userData.email,
        name: userData.name,
      }));
    } else if (userIsError) {
      console.error('Error fetching logged in user data:', userError);
    }
  }, [userData, userIsSuccess, userIsError, userError, dispatch]);

  const handleEdit = async (user) => {
    try {
      await updateUser({ id: user.id, user, access_token }).unwrap();
      refetchUsers();
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const handleDelete = async (userId) => {
    try {
      await deleteUser({ id: userId, access_token }).unwrap();
      refetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  useEffect(() => {
    if (usersIsError) {
      console.error('Error fetching users data:', usersError);
    }
  }, [usersIsError, usersError]);

  return (
    <>
      <CssBaseline />
      <Grid container>
        <Grid item sm={4} sx={{ backgroundColor: 'gray', p: 5, color: 'white' }}>
          <h1>Dashboard</h1>
          <Typography variant='h5'>Email: {userData?.email}</Typography>
          <Typography variant='h6'>Name: {userData?.name}</Typography>
          <Button variant='contained' color='warning' size='large' onClick={handleLogout} sx={{ mt: 8 }}>Logout</Button>

          <SendInvite/>
          
        </Grid>
        <Grid item sm={8}>
          <ChangePassword />
          <h2>All Users</h2>
          {usersIsSuccess ? (
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {usersData.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <TextField
                        defaultValue={user.name}
                        onBlur={(e) => handleEdit({ ...user, name: e.target.value })}
                      />
                    </TableCell>
                    <TableCell>
                      <TextField
                        defaultValue={user.email}
                        onBlur={(e) => handleEdit({ ...user, email: e.target.value })}
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleEdit(user)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDelete(user.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <Typography variant='h6'>Loading users...</Typography>
          )}
          {usersIsError && (
            <Typography variant='h6' color='error'>Error fetching users: {usersError.data?.detail || usersError.error}</Typography>
          )}
        </Grid>
      </Grid>
    </>
  );
};

export default Dashboard;
