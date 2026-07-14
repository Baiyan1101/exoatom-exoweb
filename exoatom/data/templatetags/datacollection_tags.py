from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def dataset_note(dataset_name):
    name = str(dataset_name).lower()
    if name == "nist":
        return "This data collection is critically evaluated and recommended for accuracy."
    if name == "kurucz":
        return "This data collection is designed for completeness."
    return "This data collection is provided in ExoMol atomic format."


@register.simple_tag
def preview_url(link):
    return reverse("data_file_preview", kwargs={"file_path": link.url})


@register.simple_tag
def download_url(link):
    return reverse("data_file_download", kwargs={"file_path": link.url})


@register.simple_tag
def link_metadata(link, metadata):
    if link.url.endswith(".json"):
        return ""
    if link.url.endswith(".pf"):
        max_T = int(
            metadata["dataset"]["partition_function"]["max_partition_function_temperature"]
        )
        return mark_safe(f"<ul><li>Max temperature: {max_T} K</li></ul>")
    if link.url.endswith(".states"):
        number_of_states = int(metadata["dataset"]["states"]["number_of_states"])
        max_energy = float(metadata["dataset"]["states"]["max_energy"])
        return mark_safe(f"""<ul>
            <li>Number of states: {number_of_states}</li>
            <li>Max energy: {max_energy} cm-1</li>
            </ul>""")
    if link.url.endswith(".trans"):
        number_of_transitions = int(
            metadata["dataset"]["transitions"]["number_of_transitions"]
        )
        max_wavenumber = float(metadata["dataset"]["transitions"]["max_wavenumber"])
        return mark_safe(f"""<ul>
            <li>Number of transitions: {number_of_transitions}</li>
            <li>Max wavenumber: {max_wavenumber} cm-1</li>
            </ul>""")
    return ""
