import { useChatContext } from '../context/ChatContext';

export const useTheme = () => {
  const { theme, toggleTheme } = useChatContext();
  return { theme, toggleTheme, isDark: theme === 'dark' };
};
export default useTheme;
