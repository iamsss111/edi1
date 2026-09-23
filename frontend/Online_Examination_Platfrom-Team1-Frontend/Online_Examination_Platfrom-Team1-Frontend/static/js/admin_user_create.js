document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('create-user-form');

  if (!form) return;

  form.addEventListener('submit', createUser);
});

async function createUser(event) {
  event.preventDefault();

  const firstName = document.getElementById('firstName').value.trim();
  const lastName = document.getElementById('lastName').value.trim();
  const email = document.getElementById('email').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const role = document.getElementById('role').value;
  const password = document.getElementById('password').value;

  if (!firstName || !lastName || !email || !role || !password) {
    showToast('Please fill in all required fields.', 'error');
    return;
  }

  if (password.length < 8) {
    showToast('Password must be at least 8 characters long.', 'error');
    return;
  }

  const submitButton = event.target.querySelector('button[type="submit"]');

  if (submitButton) {
    submitButton.disabled = true;
  }

  try {
    const response = await apiRequest('/admin/users', {
      method: 'POST',
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone: phone || null,
        password: password,
        role: role
      })
    });

    if (!response?.success) {
      throw new Error(
        response?.message || 'Failed to create user.'
      );
    }

    showToast(
      response.message || 'User created successfully.',
      'success'
    );

    setTimeout(() => {
      window.location.href = '/admin/users/list.html';
    }, 800);

  } catch (error) {
    console.error('Failed to create user:', error);

    showToast(
      error.message || 'Failed to create user.',
      'error'
    );

  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
}