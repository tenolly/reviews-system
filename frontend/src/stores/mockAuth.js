import { computed, ref } from 'vue'

const profiles = {
  guest: {
    id: null,
    fullName: 'Гость',
    role: 'guest',
    email: null,
    banned: false,
    avatar: 'https://i.pravatar.cc/80?img=8'
  },
  user: {
    id: 101,
    fullName: 'Анна Иванова',
    role: 'user',
    email: 'anna@example.com',
    banned: false,
    avatar: 'https://i.pravatar.cc/80?img=32'
  },
  admin: {
    id: 1,
    fullName: 'Администратор',
    role: 'admin',
    email: 'admin@example.com',
    banned: false,
    avatar: 'https://i.pravatar.cc/80?img=15'
  },
  banned: {
    id: 202,
    fullName: 'Иван Петров',
    role: 'user',
    email: 'ivan@example.com',
    banned: true,
    avatar: 'https://i.pravatar.cc/80?img=55'
  }
}

const currentProfileKey = ref('guest')

export function useAuthStore() {
  const profileKey = computed(() => currentProfileKey.value)
  const user = computed(() => profiles[currentProfileKey.value])
  const isAuthenticated = computed(() => user.value.role !== 'guest' && !user.value.banned)
  const isAdmin = computed(() => user.value.role === 'admin')

  const switchProfile = (key) => {
    if (profiles[key]) {
      currentProfileKey.value = key
    }
  }

  return {
    profiles,
    profileKey,
    user,
    isAuthenticated,
    isAdmin,
    switchProfile
  }
}

export function getAuthSnapshot() {
  const user = profiles[currentProfileKey.value]
  const isAuthenticated = user.role !== 'guest' && !user.banned
  const isAdmin = user.role === 'admin'

  return {
    user,
    isAuthenticated,
    isAdmin
  }
}

export function loginAs(email) {
  if (email && email.toLowerCase().includes('admin')) {
    currentProfileKey.value = 'admin'
    return profiles.admin
  }

  currentProfileKey.value = 'user'
  return profiles.user
}

export function logout() {
  currentProfileKey.value = 'guest'
}
