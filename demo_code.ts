// TypeScript demo file for LSP testing
import { User, UserService, AuthenticationError } from './user-service';

interface LoginRequest {
    email: string;
    password: string;
}

class AuthenticationManager {
    private userService: UserService;
    private currentUser: User | null = null;

    constructor(userService: UserService) {
        this.userService = userService;
    }

    async authenticate(request: LoginRequest): Promise<User> {
        try {
            // Find user by email first
            const user = await this.userService.findUserByEmail(request.email);
            if (!user) {
                throw new AuthenticationError(`User not found: ${request.email}`);
            }

            // Validate credentials (mock logic)
            if (request.password === 'wrong') {
                throw new AuthenticationError('Invalid password');
            }

            this.currentUser = user;
            return user;
        } catch (error) {
            if (error instanceof AuthenticationError) {
                throw error;
            }
            throw new AuthenticationError('Authentication failed');
        }
    }

    getCurrentUser(): User | null {
        return this.currentUser;
    }

    logout(): void {
        this.currentUser = null;
    }
}

// Usage example
async function main() {
    const userService = new UserService();
    const authManager = new AuthenticationManager(userService);

    try {
        const user = await authManager.authenticate({
            email: 'alice@example.com',
            password: 'password'
        });
        
        console.log(`Authenticated: ${user.name}`);
        console.log(`Current user: ${authManager.getCurrentUser()?.name}`);
        
        authManager.logout();
        console.log(`After logout: ${authManager.getCurrentUser()}`);
    } catch (error) {
        if (error instanceof AuthenticationError) {
            console.error(`Authentication failed: ${error.message}`);
        } else {
            console.error(`Unexpected error: ${error}`);
        }
    }
}

main();