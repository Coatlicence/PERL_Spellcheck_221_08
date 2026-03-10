#!C:/StrawberryPerl/perl/bin/perl.exe
use strict;
use warnings;
use CGI;
use utf8;
use open ':std', ':encoding(UTF-8)';
use Encode qw(decode encode);

my $cgi = CGI->new();

# Путь к словарю
my $dict_file = 'C:/xampp/cgi-bin/dictionary.txt';
# Путь по умолчанию к файлу с текстом
my $default_text_file = 'C:/xampp/cgi-bin/test.txt';

# === Получаем путь к файлу из формы или используем по умолчанию ===
my $text_file = $cgi->param('text_file_path') || $default_text_file;
eval { $text_file = decode('UTF-8', $text_file); };

# === ОБРАБОТКА ЗАМЕНЫ СЛОВА В ТЕКСТЕ ===
my $replace_word = $cgi->param('replace_word');
my $original_word = $cgi->param('original_word');
my $replacement_word = $cgi->param('replacement_word');
my $text_param = $cgi->param('text');

if ($replace_word && $original_word && $replacement_word && $text_param) {
    eval { $original_word = decode('UTF-8', $original_word); };
    eval { $replacement_word = decode('UTF-8', $replacement_word); };
    eval { $text_param = decode('UTF-8', $text_param); };
    
    $text_param =~ s/\b\Q$original_word\E\b/$replacement_word/g;
    
    open my $fh_out, '>:encoding(UTF-8)', $text_file or die "Не могу открыть файл для записи: $!";
    print $fh_out $text_param;
    close $fh_out;
}

# === ОБРАБОТКА ДОБАВЛЕНИЯ СЛОВА В СЛОВАРЬ ===
my $remember_word = $cgi->param('remember_word');
if ($remember_word) {
    eval { $remember_word = decode('UTF-8', $remember_word); };
    $remember_word = lc($remember_word);
    unless (_word_exists_in_dict($remember_word)) {
        open my $fh_out, '>>:encoding(UTF-8)', $dict_file or die "Не могу открыть файл для записи: $!";
        print $fh_out "$remember_word\n";
        close $fh_out;
    }
}

# === ОБРАБОТКА ПОЛЬЗОВАТЕЛЬСКОГО ВАРИАНТА ===
my $custom_variant = $cgi->param('custom_variant');
if ($custom_variant) {
    eval { $custom_variant = decode('UTF-8', $custom_variant); };
    $custom_variant = lc($custom_variant);
    unless (_word_exists_in_dict($custom_variant)) {
        open my $fh_out, '>>:encoding(UTF-8)', $dict_file or die "Не могу открыть файл для записи: $!";
        print $fh_out "$custom_variant\n";
        close $fh_out;
    }
}

# === ЗАГРУЗКА ТЕКСТА ИЗ ФАЙЛА ===
my $text = '';
if (-e $text_file) {
    open my $fh, '<:encoding(UTF-8)', $text_file or die "Не могу открыть файл: $!";
    local $/;
    $text = <$fh>;
    close $fh;
    eval { $text = decode('UTF-8', $text); };
}

# === ОБРАБОТКА ЗАГРУЖЕННОГО ФАЙЛА ===
my $uploaded_file = $cgi->param('file');
if ($uploaded_file) {
    my $file_handle = $cgi->upload('file');
    if ($file_handle) {
        # === Получаем имя файла ===
        my $filename = $uploaded_file;
        $filename =~ s/.*[\\\/]//;  # Убираем путь
        
        # === Пробуем декодировать UTF-8 ===
        my $decoded_filename = $filename;
        eval { $decoded_filename = decode('UTF-8', $filename); };
        
        # === Транслитерация для безопасного имени ===
        my $safe_filename = transliterate_filename($decoded_filename);
        
        # Сохраняем в cgi-bin
        my $upload_path = "C:/xampp/cgi-bin/$safe_filename";
        
        local $/;
        binmode($file_handle);
        my $content = <$file_handle>;
        eval { $content = decode('UTF-8', $content); };
        $text = $content;
        
        open my $fh_out, '>:encoding(UTF-8)', $upload_path or die "Не могу открыть файл для записи: $!";
        print $fh_out $content;
        close $fh_out;
        
        # Обновляем путь к файлу
        $text_file = $upload_path;
    }
}

# === ОБРАБОТКА ТЕКСТА ИЗ TEXTAREA ===
if ($text_param && !$uploaded_file && !$replace_word) {
    $text = $text_param;
    
    open my $fh_out, '>:encoding(UTF-8)', $text_file or die "Не могу открыть файл для записи: $!";
    print $fh_out $text;
    close $fh_out;
}

# === ФУНКЦИЯ: проверка существования слова в словаре ===
sub _word_exists_in_dict {
    my ($word) = @_;
    $word = lc($word);
    open my $fh, '<:encoding(UTF-8)', $dict_file or return 0;
    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/^\s+|\s+$//g;
        return 1 if lc($line) eq $word;
    }
    close $fh;
    return 0;
}

# === ФУНКЦИЯ: Транслитерация имени файла ===
sub transliterate_filename {
    my ($filename) = @_;
    return 'untitled.txt' unless defined $filename && $filename ne '';
    
    # Таблица транслитерации
    my %translit = (
        'а' => 'a', 'б' => 'b', 'в' => 'v', 'г' => 'g', 'д' => 'd',
        'е' => 'e', 'ё' => 'yo', 'ж' => 'zh', 'з' => 'z', 'и' => 'i',
        'й' => 'y', 'к' => 'k', 'л' => 'l', 'м' => 'm', 'н' => 'n',
        'о' => 'o', 'п' => 'p', 'р' => 'r', 'с' => 's', 'т' => 't',
        'у' => 'u', 'ф' => 'f', 'х' => 'h', 'ц' => 'ts', 'ч' => 'ch',
        'ш' => 'sh', 'щ' => 'sch', 'ъ' => '', 'ы' => 'y', 'ь' => '',
        'э' => 'e', 'ю' => 'yu', 'я' => 'ya',
        'А' => 'A', 'Б' => 'B', 'В' => 'V', 'Г' => 'G', 'Д' => 'D',
        'Е' => 'E', 'Ё' => 'Yo', 'Ж' => 'Zh', 'З' => 'Z', 'И' => 'I',
        'Й' => 'Y', 'К' => 'K', 'Л' => 'L', 'М' => 'M', 'Н' => 'N',
        'О' => 'O', 'П' => 'P', 'Р' => 'R', 'С' => 'S', 'Т' => 'T',
        'У' => 'U', 'Ф' => 'F', 'Х' => 'H', 'Ц' => 'Ts', 'Ч' => 'Ch',
        'Ш' => 'Sh', 'Щ' => 'Sch', 'Ъ' => '', 'Ы' => 'Y', 'Ь' => '',
        'Э' => 'E', 'Ю' => 'Yu', 'Я' => 'Ya',
    );
    
    # Заменяем русские буквы
    $filename =~ s/([а-яА-ЯёЁ])/exists $translit{$1} ? $translit{$1} : $1/ge;
    
    # Заменяем спецсимволы на подчёркивание
    $filename =~ s/[^a-zA-Z0-9._-]/_/g;
    
    # Убираем множественные подчёркивания
    $filename =~ s/_+/_/g;
    
    return $filename || 'untitled.txt';
}

# === Заголовок ответа ===
print $cgi->header(
    -type    => 'text/html',
    -charset => 'utf-8'
);

# === HTML начало с встроенными стилями ===
print <<'HTML';
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Проверка орфографии</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f2f5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .main-title {
            font-size: 36px;
            color: #2c3e50;
            margin: 0;
            font-weight: bold;
            text-align: center;
        }
        .variant {
            font-size: 24px;
            color: #3498db;
            margin: 10px 0;
            font-weight: normal;
        }
        .info-text {
            font-size: 18px;
            color: #7f8c8d;
            margin: 20px 0;
            text-align: center;
        }
        .form-container {
            margin: 30px 0;
            text-align: center;
        }
        textarea {
            width: 90%;
            max-width: 800px;
            height: 150px;
            padding: 15px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            font-size: 16px;
            resize: vertical;
            margin-bottom: 15px;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 18px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .dict-button {
            background-color: #2ecc71;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 18px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 15px;
            transition: background-color 0.3s;
            width: 90%;
            max-width: 800px;
        }
        .dict-button:hover {
            background-color: #27ae60;
        }
        .result-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        th {
            background-color: #34495e;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 16px;
            border: 1px solid #2c3e50;
        }
        td {
            padding: 12px 15px;
            text-align: center;
            border: 1px solid #bdc3c7;
            font-size: 16px;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .status-present {
            background-color: #d5f5e3;
            color: #27ae60;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            border: 1px solid #27ae60;
        }
        .status-absent {
            background-color: #fadbd8;
            color: #e74c3c;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            border: 1px solid #e74c3c;
        }
        .no-results {
            text-align: center;
            font-size: 18px;
            color: #7f8c8d;
            margin: 30px 0;
            font-style: italic;
        }
        .summary {
            text-align: center;
            font-size: 20px;
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
        }
        .summary-error {
            background-color: #fadbd8;
            color: #e74c3c;
        }
        .summary-success {
            background-color: #d5f5e3;
            color: #27ae60;
        }
        input[type="file"] {
            margin: 10px 0;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .suggest-btn, .remember-btn {
            padding: 5px 10px;
            margin: 2px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .suggest-btn {
            background-color: #f39c12;
            color: white;
        }

        .remember-btn {
            background-color: #9b59b6;
            color: white;
        }

        .suggest-btn:hover {
            background-color: #d35400;
        }

        .remember-btn:hover {
            background-color: #8e44ad;
        }
        .file-info {
            background-color: #e8f4f8;
            padding: 10px 15px;
            border-radius: 6px;
            margin: 15px 0;
            font-size: 14px;
            color: #2980b9;
        }
    </style>
</head>
<body>
HTML

print '<div class="container">';
print '<div class="header">';
print '<h1 class="main-title">Проверка орфографии</h1>';
print '<div class="variant">Работу выполнил ст. гр. 22ВП1 Резяков И. Р.</div>';
print '<div class="info-text">Введите текст для проверки его наличия в словаре</div>';

# === Информация о текущем файле ===
my $file_name = $text_file;
$file_name =~ s/.*[\\\/]//;  # Оставляем только имя файла
print '<div class="file-info">📁 Текущий файл: <strong>' . escape_html($file_name) . '</strong></div>';

print '</div>';

# === Форма ===
print '<div class="form-container">';
print $cgi->start_form(-method => 'POST', -enctype => 'multipart/form-data', -id => 'main_form');

# === Скрытое поле с путём к файлу ===
print '<input type="hidden" name="text_file_path" value="' . escape_html($text_file) . '">';

print '<textarea name="text" id="text_area" rows="10" style="width:90%;max-width:800px;padding:15px;border:2px solid #bdc3c7;border-radius:8px;font-size:16px;resize:vertical;margin-bottom:15px;">' . escape_html($text) . '</textarea>';
print $cgi->br();

print $cgi->submit(-value => 'Проверить орфографию', -class => 'dict-button');
print $cgi->br();

print '<label for="file">Выберите файл:</label>';
print $cgi->filefield(-name => 'file', -id => 'file', -size => 50);
print $cgi->br();

print $cgi->submit(-value => 'Проверить файл', -class => 'dict-button');

print $cgi->end_form();

print '<a href="dictionary_editor.pl" class="dict-button">Редактировать словарь</a>';
print '</div>';

if ($text) {
    my @results = check_spelling_with_positions($text);
    
    if (@results) {
        print display_results_table($text_file, @results);
    } else {
        print '<div class="no-results">Текст не содержит слов для проверки</div>';
    }
}

print '</div>';

# === JavaScript ===
print <<'JSCRIPT';
<script>
// Синхронизация скрытых полей для формы "Заменить"
function syncHiddenFieldForForm(form) {
    var textarea = document.getElementById('text_area');
    var mainForm = document.getElementById('main_form');
    
    if (textarea) {
        var textField = form.querySelector('.form_text_field');
        if (textField) {
            textField.value = textarea.value;
        }
    }
    
    // Копируем путь к файлу из главной формы
    if (mainForm) {
        var filePathField = mainForm.querySelector('input[name="text_file_path"]');
        if (filePathField) {
            var formFilePathField = form.querySelector('.form_file_path_field');
            if (formFilePathField) {
                formFilePathField.value = filePathField.value;
            }
        }
    }
}

// Автоматическая синхронизация всех форм при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            syncHiddenFieldForForm(form);
        });
    });
});
</script>
JSCRIPT

print '</body></html>';

# ========================================
# Функции программы
# ========================================

sub load_dictionary {
    my %dict;
    open my $fh, '<:encoding(UTF-8)', $dict_file or die "Не могу открыть словарь: $!";
    
    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/^\s+|\s+$//g;
        next if $line eq '';
        $dict{lc($line)} = 1;
    }
    
    close $fh;
    return %dict;
}

sub levenshtein {
    my ($s, $t) = @_;
    my $len_s = length($s);
    my $len_t = length($t);
    
    return $len_t if $len_s == 0;
    return $len_s if $len_t == 0;
    
    my @d;
    $d[$_][0] = $_ for (0..$len_s);
    $d[0][$_] = $_ for (0..$len_t);
    
    for my $i (1..$len_s) {
        for my $j (1..$len_t) {
            my $cost = (substr($s, $i-1, 1) eq substr($t, $j-1, 1)) ? 0 : 1;
            $d[$i][$j] = min(
                $d[$i-1][$j] + 1,
                $d[$i][$j-1] + 1,
                $d[$i-1][$j-1] + $cost
            );
        }
    }
    return $d[$len_s][$len_t];
}

sub min {
    return $_[0] < $_[1] ? ($_[0] < $_[2] ? $_[0] : $_[2]) : ($_[1] < $_[2] ? $_[1] : $_[2]);
}

sub calculate_similarity {
    my ($word, $dict_word) = @_;
    my $dist = levenshtein($word, $dict_word);
    my $max_len = (length($word) > length($dict_word)) ? length($word) : length($dict_word);
    return 1 - ($dist / $max_len);
}

sub find_best_suggestion {
    my ($word, $dictionary) = @_;
    
    my $best_word = '';
    my $best_similarity = 0;
    my $len = length($word);
    my $max_diff = int(0.2 * $len);
    
    foreach my $dict_word (keys %$dictionary) {
        my $dict_len = length($dict_word);
        next if abs($len - $dict_len) > $max_diff;
        
        my $similarity = calculate_similarity($word, $dict_word);
        
        if ($similarity >= 0.8 && $similarity > $best_similarity) {
            $best_similarity = $similarity;
            $best_word = $dict_word;
        }
    }
    
    return $best_word;
}

sub check_spelling_with_positions {
    my ($text) = @_;
    my %dictionary = load_dictionary();
    my @results;
    my $word_number = 1;
    my $pos = 0;
    
    while ($pos < length($text)) {
        my $char = substr($text, $pos, 1);
        
        if ($char =~ /\s/) {
            while ($pos < length($text) && substr($text, $pos, 1) =~ /\s/) { $pos++; }
        } elsif ($char =~ /\p{L}/) {
            my $word = '';
            while ($pos < length($text) && substr($text, $pos, 1) =~ /\p{L}/) {
                $word .= substr($text, $pos, 1);
                $pos++;
            }
            
            my $is_known = exists $dictionary{lc($word)};
            my $suggestion = '';
            my $similarity_percent = '';
            
            if (!$is_known) {
                $suggestion = find_best_suggestion(lc($word), \%dictionary);
                if ($suggestion) {
                    my $similarity = calculate_similarity(lc($word), $suggestion);
                    $similarity_percent = sprintf("%.0f", $similarity * 100) . '%';
                }
            }
            
            push @results, {
                number => $word_number++,
                text   => $word,
                known  => $is_known,
                suggestion => $suggestion,
                similarity => $similarity_percent
            };
        } else {
            while ($pos < length($text) && substr($text, $pos, 1) !~ /\s/ && substr($text, $pos, 1) !~ /\p{L}/) {
                $pos++;
            }
        }
    }
    
    return @results;
}

sub display_results_table {
    my ($text_file_path, @results) = @_;
    
    my $present_count = 0;
    my $absent_count = 0;
    foreach my $result (@results) {
        if ($result->{known}) {
            $present_count++;
        } else {
            $absent_count++;
        }
    }
    
    my $summary_class = $absent_count == 0 ? 'summary-success' : 'summary-error';
    my $summary_text = $absent_count == 0 ? 
        "✅ Все $present_count слов(а) найдены в словаре!" : 
        "⚠️ $absent_count слов(а) не найдены в словаре, $present_count слов(а) найдены";
    
    my $table = '<div class="summary ' . $summary_class . '">' . $summary_text . '</div>';
    $table .= '<table class="result-table">';
    $table .= '<thead><tr><th>№</th><th>Слово из текста</th><th>Статус</th><th>Предложение</th><th>Действия</th><th>Свой вариант</th></tr></thead>';
    $table .= '<tbody>';
    
    foreach my $result (@results) {
        my $status_class = $result->{known} ? 'status-present' : 'status-absent';
        my $status_text = $result->{known} ? 'Присутствует' : 'Отсутствует';
        
        $table .= '<tr>';
        $table .= '<td>' . $result->{number} . '</td>';
        $table .= '<td>' . escape_html($result->{text}) . '</td>';
        $table .= '<td><span class="' . $status_class . '">' . $status_text . '</span></td>';
        
        $table .= '<td>';
        if ($result->{suggestion}) {
            $table .= '<strong>' . escape_html($result->{suggestion}) . '</strong>';
            $table .= '<div style="font-size:12px;color:#7f8c8d;margin-top:2px;">(' . $result->{similarity} . ')</div>';
        } elsif (!$result->{known}) {
            $table .= '<em>Нет предложений</em>';
        } else {
            $table .= '—';
        }
        $table .= '</td>';
        
        $table .= '<td>';
        if (!$result->{known}) {
            if ($result->{suggestion}) {
                $table .= qq{
                    <form method="POST" style="display:inline;" onsubmit="syncHiddenFieldForForm(this);">
                        <input type="hidden" name="text" class="form_text_field" value="">
                        <input type="hidden" name="text_file_path" class="form_file_path_field" value="">
                        <input type="hidden" name="original_word" value="} . escape_html($result->{text}) . qq{">
                        <input type="hidden" name="replacement_word" value="} . escape_html($result->{suggestion}) . qq{">
                        <button type="submit" name="replace_word" value="1" class="suggest-btn">Заменить</button>
                    </form>
                };
            } else {
                $table .= '<button class="suggest-btn" disabled style="opacity:0.5;cursor:not-allowed;">Заменить</button> ';
            }
            
            $table .= qq{
                <form method="POST" style="display:inline;">
                    <input type="hidden" name="text_file_path" value="} . escape_html($text_file_path) . qq{">
                    <button type="submit" name="remember_word" value="} . escape_html($result->{text}) . qq{" class="remember-btn">Запомнить</button>
                </form>
            };
        } else {
            $table .= '—';
        }
        $table .= '</td>';
        
        $table .= '<td>';
        if (!$result->{known}) {
            $table .= qq{
                <form method="POST" style="display:inline;">
                    <input type="hidden" name="text_file_path" value="} . escape_html($text_file_path) . qq{">
                    <input type="text" name="custom_variant" value="" size="12" style="padding:3px;margin-right:3px;">
                    <button type="submit" class="remember-btn">Подтвердить</button>
                </form>
            };
        } else {
            $table .= '—';
        }
        $table .= '</td>';
        
        $table .= '</tr>';
    }
    
    $table .= '</tbody></table>';
    return $table;
}

sub escape_html {
    my $text = shift;
    return '' unless defined $text;
    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    $text =~ s/"/&quot;/g;
    return $text;
}
