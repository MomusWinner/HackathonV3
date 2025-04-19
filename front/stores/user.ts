import { defineStore } from "pinia";
import { v4 as uuidv4 } from "uuid";

export const useUserStore = defineStore("user", () => {
	const user = ref<string>();

	function setUser(newUser: string) {
		user.value = newUser;
		localStorage.setItem("user", user.value);
	}

	function getUser(): string {
		if (!user.value) {
			const localUser = localStorage.getItem("user");
			if (!localUser) {
				setUser(uuidv4());
			} else {
				setUser(localUser);
			}
		}
		return user.value!;
	}

	return {
		setUser,
		getUser,
	};
});
