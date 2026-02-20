import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { KindeProvider } from '@kinde-oss/kinde-auth-react';
import App from './App';
import './index.css';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
    <KindeProvider
        clientId={import.meta.env.VITE_KINDE_CLIENT_ID}
        domain={import.meta.env.VITE_KINDE_DOMAIN}
        logoutUri={import.meta.env.VITE_KINDE_LOGOUT_URL}
        redirectUri={import.meta.env.VITE_KINDE_REDIRECT_URL}
    >
        <QueryClientProvider client={queryClient}>
            <App />
        </QueryClientProvider>
    </KindeProvider>
);
