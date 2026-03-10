#!C:/StrawberryPerl/perl/bin/perl.exe
use strict;
use warnings;
use CGI;
use utf8;
use open ':std', ':encoding(UTF-8)';
use URI::Escape;

my $cgi = CGI->new();
my $action = $cgi->param('action') || '';
my $message = $cgi->param('message') || '';

# Обработка POST-запросов
if ($cgi->request_method eq 'POST') {
    my $result_message = '';
    
    if ($action eq 'add') {
        $result_message = handle_add($cgi);
    } elsif ($action eq 'delete') {
        $result_message = handle_delete($cgi);
    } elsif ($action eq 'save') {
        $result_message = handle_save($cgi);
    }
    
    print $cgi->redirect("dictionary_editor.pl");
    exit;
}

# Заголовок ответа
print $cgi->header(
    -type    => 'text/html',
    -charset => 'utf-8'
);

# Вывод HTML страницы
print <<'HTML';
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Редактор словаря</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f2f5;
        }
        .container {
            max-width: 800px;
            margin: 50px auto;
            padding: 30px;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-top: 0;
        }
        .add-form {
            margin: 20px 0;
            text-align: center;
        }
        .add-form input {
            padding: 8px 15px;
            width: 300px;
            margin-right: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .add-form button {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .word-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .word-table th {
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }
        .word-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        .word-cell {
            font-weight: 500;
            color: #2c3e50;
            font-size: 16px;
        }
        .action-cell {
            text-align: right;
        }
        .edit-btn, .delete-btn {
            padding: 5px 10px;
            margin: 0 3px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 14px;
        }
        .edit-btn {
            background-color: #3498db;
            color: white;
        }
        .delete-btn {
            background-color: #e74c3c;
            color: white;
            border: none;
            cursor: pointer;
        }
        .cancel-btn, .accept-btn {
            padding: 5px 10px;
            margin: 0 3px;
            border-radius: 4px;
            font-size: 14px;
        }
        .cancel-btn {
            background-color: #95a5a6;
            color: white;
        }
        .accept-btn {
            background-color: #2ecc71;
            color: white;
        }
        .message {
            padding: 10px 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            background-color: #d5f5e3;
            color: #27ae60;
            text-align: center;
        }
        .error {
            background-color: #fadbd8;
            color: #e74c3c;
        }
        .empty {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 20px;
            font-size: 18px;
        }
        .back-link {
            text-align: center;
            margin-top: 30px;
        }
        .back-link a {
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }
        .back-btn {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
            display: block;
            width: 100%;
            text-align: center;
        }
        .back-btn:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
HTML

print '<div class="back-link">';
print '<a href="spellcheck.cgi">← Вернуться к проверке орфографии</a>';
print '</div>';

print '<div class="container">';
print '<h1>Редактор словаря</h1>';

# Сообщение об операции
# Удалите или закомментируйте эту часть - сообщения больше не выводятся
# if ($message) {
#     print '<div class="message">' . $message . '</div>';
# }

# Форма добавления нового слова
print '<div class="add-form">';
print $cgi->start_form(-method => 'POST');
print $cgi->hidden(-name => 'action', -value => 'add');
print '<input type="text" name="word" placeholder="Новое слово" autofocus>';
print '<button type="submit">Добавить слово</button>';
print $cgi->end_form();
print '</div>';

# Загрузка словаря
my @dictionary = load_dictionary();
@dictionary = sort { lc($a) cmp lc($b) } @dictionary;

# Таблица со словами
if (@dictionary) {
    print '<table class="word-table">';
    print '<thead><tr><th>Слово</th><th>Действия</th></tr></thead>';
    print '<tbody>';
    
    foreach my $word (@dictionary) {
        # Обычный режим
        print '<tr>';
        print '<td class="word-cell">' . $word . '</td>';
        print '<td class="action-cell">';
        print '<button class="edit-btn" onclick="editWord(\'' . $word . '\')">Редактировать</button> ';
        print $cgi->start_form(-method => 'POST', -style => 'display:inline;');
        print $cgi->hidden(-name => 'action', -value => 'delete');
        print $cgi->hidden(-name => 'word', -value => $word);
        print '<button type="submit" class="delete-btn">Удалить</button>';
        print $cgi->end_form();
        print '</td></tr>';
        
        # Форма редактирования (скрыта по умолчанию)
        print '<tr id="edit-row-' . $word . '" style="display:none;">';
        print '<td colspan="2">';
        print $cgi->start_form(-method => 'POST');
        print $cgi->hidden(-name => 'action', -value => 'save');
        print $cgi->hidden(-name => 'old_word', -value => $word);
        print '<input type="text" name="new_word" value="' . $word . '">';
        print '<button type="submit" class="accept-btn">Принять</button>';
        print '<button type="button" class="cancel-btn" onclick="cancelEdit(\'' . $word . '\')">Отмена</button>';
        print $cgi->end_form();
        print '</td></tr>';
    }
    
    print '</tbody></table>';
} else {
    print '<p class="empty">Словарь пуст. Добавьте первое слово!</p>';
}

print '<div class="back-link">';
print '<a href="spellcheck.pl">← Вернуться к проверке орфографии</a>';
print '</div>';

print '</div>'; # container

# JavaScript для управления режимами редактирования
print <<'JS';
<script>
    function editWord(word) {
        // Скрыть все строки редактирования
        var editRows = document.querySelectorAll('[id^="edit-row-"]');
        for (var i = 0; i < editRows.length; i++) {
            editRows[i].style.display = 'none';
        }
        
        // Показать строку редактирования для текущего слова
        var editRow = document.getElementById('edit-row-' + word);
        if (editRow) {
            editRow.style.display = '';
        }
        
        // Скрыть строку с текущим словом
        var wordRow = editRow.previousElementSibling;
        if (wordRow) {
            wordRow.style.display = 'none';
        }
    }
    
    function cancelEdit(word) {
        // Показать строку с текущим словом
        var editRow = document.getElementById('edit-row-' + word);
        if (editRow) {
            var wordRow = editRow.previousElementSibling;
            if (wordRow) {
                wordRow.style.display = '';
            }
            editRow.style.display = 'none';
        }
    }
</script>
JS

print '</body></html>';

# ========================================
# Функции программы
# ========================================

# Загрузка словаря
sub load_dictionary {
    my @words;
    open my $fh, '<:encoding(UTF-8)', 'C:/xampp/cgi-bin/dictionary.txt' or return ();
    
    while (my $line = <$fh>) {
        chomp $line;
        push @words, $line if $line ne '';
    }
    
    close $fh;
    return @words;
}

# Сохранение словаря
sub save_dictionary {
    my @words = @_;
    open my $fh, '>:encoding(UTF-8)', 'C:/xampp/cgi-bin/dictionary.txt' or return "Ошибка сохранения";
    
    print $fh "$_\n" for @words;
    close $fh;
    
    return "Словарь успешно обновлен";
}

# Обработка добавления слова
sub handle_add {
    my ($cgi) = @_;
    my $word = $cgi->param('word') || '';
    
    return "Слово не может быть пустым" unless $word;
    
    my @dictionary = load_dictionary();
    push @dictionary, $word;
    return save_dictionary(@dictionary);
}

# Обработка удаления
sub handle_delete {
    my ($cgi) = @_;
    my $word_to_delete = $cgi->param('word') || '';
    
    return "Не указано слово для удаления" unless $word_to_delete;
    
    my @dictionary = load_dictionary();
    my @new_dictionary = grep { $_ ne $word_to_delete } @dictionary;
    
    return save_dictionary(@new_dictionary);
}

# Обработка редактирования
sub handle_save {
    my ($cgi) = @_;
    my $old_word = $cgi->param('old_word') || '';
    my $new_word = $cgi->param('new_word') || '';
    
    return "Новое слово не может быть пустым" unless $new_word;
    
    my @dictionary = load_dictionary();
    
    # Замена слова
    for (my $i = 0; $i < @dictionary; $i++) {
        if ($dictionary[$i] eq $old_word) {
            $dictionary[$i] = $new_word;
            last;
        }
    }
    
    return save_dictionary(@dictionary);
}
