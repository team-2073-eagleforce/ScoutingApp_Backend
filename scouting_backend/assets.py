from flask import current_app as app
from flask_assets import Bundle


def compile_static_assets(assets):
    assets.auto_build = True
    assets.debug = False
    common_style_bundle = Bundle(

    )
    home_style_bundle = Bundle(

    )
    retrieval_style_bundle = Bundle(

    )
    analysis_style_bundle = Bundle(

    )
    assets.register("common_style_bundle", common_style_bundle)
    assets.register("home_style_bundle", home_style_bundle)
    assets.register("retrieval_style_bundle", retrieval_style_bundle)
    assets.register("analysis_style_bundle", analysis_style_bundle)
    if app.config["FLASK_ENV"] == "development":
        common_style_bundle.build()
        home_style_bundle.build()
        retrieval_style_bundle.build()
        analysis_style_bundle.build()
    return assets
