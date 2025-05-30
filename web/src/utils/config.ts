import packageJson from '../../package.json';

const { version, name } = packageJson;

type EnvType = string | Promise<string> | number | string[] | boolean;

function env(key: string, fallback: string): string;
function env(key: string, fallback: Promise<string>): Promise<string>;

function env(key: string, fallback: number): number;

function env(key: string, fallback: string[]): string[];

function env(key: string, fallback: boolean): boolean;

function env(key: string, fallback: EnvType): EnvType {
  const value = import.meta.env[`VITE_${key}`];
  if (typeof fallback === 'string') {
    return value ?? fallback;
  }
  if (typeof fallback === 'number') {
    return Number.parseFloat(env(key, fallback.toString()));
  }
  if (typeof fallback === 'boolean') {
    return value !== undefined ? value === 'true' : fallback
  }
  if (Array.isArray(fallback)) {
    return value?.split(';;') ?? fallback;
  }
  return Promise.resolve(value ?? fallback);
}

const config = {
  APP_NAME: env('APP_NAME', name),
  APP_VERSION: version,
  GET_MODEL_URL: env('GET_MODEL_URL', 'https://vewdtihoome2nky4pe47te2dvm0ymmch.lambda-url.ap-southeast-2.on.aws'),
};

export default config;