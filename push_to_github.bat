@echo off
chcp 65001 >nul
echo Инициализация Git-репозитория...
git init

echo.
echo Добавление файлов в индекс...
git add .

echo.
echo Создание коммита...
git commit -m "Initial commit of Gym Telegram Bot"

echo.
echo Перейди на GitHub: https://github.com/new
echo Создай новый пустой репозиторий (БЕЗ файла README, .gitignore или license).
echo Скопируй HTTPS ссылку на него (например, https://github.com/твое_имя/твой_проект.git)
echo.
set /p REPO_URL="Вставь ссылку на репозиторий сюда и нажми Enter: "

git branch -M main
git remote add origin %REPO_URL%

echo.
echo Отправляем код на GitHub...
git push -u origin main

echo.
echo Готово! Код успешно загружен на GitHub. Теперь можешь скачивать его на свой сервер (git clone ...).
pause
