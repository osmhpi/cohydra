{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}
    :members:
    :undoc-members:
    :inherited-members:

    .. autopackagesummary:: {{ fullname }}
        :toctree: .
        :template: autosummary/package.rst

    {% if functions %}
    .. rubric:: Functions

    .. autosummary::
        :nosignatures:
    {% for item in functions %}
        {{ item }}
    {%- endfor %}
    {% endif %}

    {% if classes %}
    .. rubric:: Classes

    .. autosummary::
        :nosignatures:
    {% for item in classes %}
        {{ item }}
    {%- endfor %}
    {% endif %}

    {% if exceptions %}
    .. rubric:: Exceptions

    .. autosummary::
        :nosignatures:
    {% for item in exceptions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    
    |

{% if classes %}
.. rubric:: Inheritance Diagramm

.. inheritance-diagram:: {{ fullname }}

|
{% endif %}
