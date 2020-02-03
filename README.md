INGInious plugin for fill-in-the-blanks code problems
=====================================================

This plugins define a new problem type named `code_fill` that can accept some code with holes in it. Only the holes will be editable by the students.

For example, with the following default value, only the second parameter name and the method body can be modified bu the students

```java
public static void main(String[] {%argv%}) {{%
    // TODO
%}}
```

As a bonus, the hole for the method name will not allow line breaks. These are only allowed when the hole opening and closing tags (`{%` and `%}`) are on different lines.

## Installing

    pip3 install git+https://github.com/UCL-INGI/INGInious-problems-code-fill

## Activating

In your ``configuration.yaml`` file, add the following plugin entry:

    plugins:
      - plugin_module: "inginious-problems-code-fill"
