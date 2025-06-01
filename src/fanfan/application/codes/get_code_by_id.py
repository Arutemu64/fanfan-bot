from fanfan.adapters.db.repositories.codes import CodesRepository
from fanfan.core.exceptions.codes import CodeNotFound
from fanfan.core.models.code import Code
from fanfan.core.vo.code import CodeId


class GetCodeById:
    def __init__(self, codes_repo: CodesRepository):
        self.codes_repo = codes_repo

    async def __call__(self, code_id: CodeId) -> Code:
        if code := await self.codes_repo.get_code_by_id(code_id):
            return code
        raise CodeNotFound
