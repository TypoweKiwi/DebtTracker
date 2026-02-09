start:
	powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

start-sqlite:
	powershell -ExecutionPolicy Bypass -File scripts/dev.ps1 -Db sqlite

start-supabase:
	powershell -ExecutionPolicy Bypass -File scripts/dev.ps1 -Db supabase

start-mock:
	powershell -ExecutionPolicy Bypass -File scripts/dev.ps1 -Db sqlite -MockData
