import { computed, ref } from 'vue'
import { api, clearAuth } from '../services/api'

const guestUser = () => ({
	id: null,
	username: 'guest',
	fullName: 'Гость',
	email: null,
	role: 'guest',
	is_staff: false,
	banned: false,
	avatar: ''
})

const currentUser = ref(guestUser())
const loadingProfile = ref(false)
const hasFetchedProfile = ref(false)

const mapProfile = (profile) => {
	if (!profile) {
		return guestUser()
	}

	const username = profile.username || profile.email || 'user'
	return {
		id: profile.id ?? null,
		username,
		fullName: profile.full_name || profile.name || username,
		email: profile.email || null,
		role: profile.is_staff || profile.is_superuser ? 'admin' : 'user',
		is_staff: Boolean(profile.is_staff),
		banned: Boolean(profile.is_banned || profile.banned),
		avatar: profile.avatar || ''
	}
}

const setUser = (profile) => {
	currentUser.value = mapProfile(profile)
}

const resetUser = () => {
	currentUser.value = guestUser()
  clearAuth()
}

const isAuthenticated = computed(() => currentUser.value.role !== 'guest' && !currentUser.value.banned)
const isAdmin = computed(() => Boolean(currentUser.value.is_staff || currentUser.value.role === 'admin'))

const initAuth = async ({ force = false } = {}) => {
	if (loadingProfile.value) {
		return
	}
	if (hasFetchedProfile.value && !force) {
		return
	}
	if (force) {
		hasFetchedProfile.value = false
	}

	loadingProfile.value = true
	try {
		const profile = await api.fetchProfile()
		if (profile) {
			setUser(profile)
		} else {
			resetUser()
		}
		hasFetchedProfile.value = true
	} catch (error) {
		resetUser()
		clearAuth()
		console.warn('Не удалось загрузить профиль', error)
	} finally {
		loadingProfile.value = false
	}
}

const login = async ({ username, email, password }) => {
	if (!password || !(username || email)) {
		throw new Error('Укажите логин и пароль')
	}
	clearAuth()
	await api.login({ username, email, password })
	await initAuth({ force: true })
}

const register = async ({ username, password, password_confirm }) => {
	if (!password || !username) {
		throw new Error('Укажите логин и пароль')
	}
	clearAuth()
	await api.register({ username, password, password_confirm })
	await initAuth()
}

const logout = async () => {
	try {
		await api.logout()
	} finally {
		resetUser()
		clearAuth()
	}
}

export function useAuthStore() {
	return {
		user: computed(() => currentUser.value),
		isAuthenticated,
		isAdmin,
		loadingProfile,
		hasFetchedProfile,
		initAuth,
		login,
		logout,
		register
	}
}

export const getAuthSnapshot = () => ({
	user: currentUser.value,
	isAuthenticated: isAuthenticated.value,
	isAdmin: isAdmin.value
})

export const __resetAuthForTests = resetUser
