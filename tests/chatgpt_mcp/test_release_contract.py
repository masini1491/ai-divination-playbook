"""Guard the selective GitHub->ChatGPT MCP generator and policy egress."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / 'tools/build_chatgpt_mcp_release.py'
PROFILE = REPO / 'integrations/chatgpt-mcp/release_profile.json'
POLICY_ADAPTER = REPO / 'integrations/chatgpt-mcp/policy_adapter.py'

spec = importlib.util.spec_from_file_location('selective_release', BUILDER)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

spec2 = importlib.util.spec_from_file_location('selective_policy_adapter', POLICY_ADAPTER)
policy_adapter = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(policy_adapter)


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()

class SelectiveReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        p = self.repo/'integrations/chatgpt-mcp'
        p.mkdir(parents=True)
        shutil.copy2(PROFILE, p/'release_profile.json')
        for file in builder._ALLOWED_ENGINE_FILES:
            dest = self.repo/file
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text('# intentionally small exact test engine\n',encoding='utf-8')
        for file in builder._ALLOWED_POLICY_FILES:
            (self.repo/file).write_text('# '+file+'\nAuthoritative text for '+file+'\n',encoding='utf-8')
        (self.repo/'PALMISTRY.md').write_text('# unrelated new hand-reading features\n',encoding='utf-8')
        git(self.repo, 'init', '-q', '-b', 'main')
        git(self.repo, 'config', 'user.email', 'ci-tests@example.invalid')
        git(self.repo, 'config', 'user.name', 'CI Fixture')
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-qm', 'fixture')

    def test_only_exact_allowed_methods(self):
        files=builder.generate(self.repo)
        self.assertEqual(len(files), 8)
        for p in files:
            self.assertNotIn('palmistry',p.lower())
            self.assertNotIn('astrology',p.lower())
        pack=json.loads(files['policy_pack.json'])
        self.assertEqual(set(pack['owners']),set(builder._ALLOWED_POLICY_FILES))
        self.assertNotIn('PALMISTRY.md',pack['owners'])

    def test_sync_then_check(self):
        self.assertEqual(builder.sync(self.repo,check=False),0)
        self.assertEqual(builder.sync(self.repo,check=True),0)
        self.assertTrue((self.repo/'integrations/chatgpt-mcp/canonical-repo/runtime/casting/core.py').exists())

    def test_source_dirty_blocks_build(self):
        with (self.repo/'runtime/casting/core.py').open('a') as f: f.write('modified\n')
        with self.assertRaisesRegex(ValueError,'UNCOMMITTED_CANONICAL_SOURCE'):
            builder.generate(self.repo)

    def test_policy_dirty_blocks_build(self):
        with (self.repo/'LIUYAO.md').open('a') as f:f.write('changed\n')
        with self.assertRaisesRegex(ValueError,'UNCOMMITTED_CANONICAL_SOURCE'):
            builder.generate(self.repo)

    def test_unapproved_method_blocks_release(self):
        profile=json.loads(PROFILE.read_text(encoding='utf8'))
        profile['enabled_methods'].append('palmistry')
        (self.repo/'integrations/chatgpt-mcp/release_profile.json').write_text(json.dumps(profile))
        with self.assertRaisesRegex(ValueError,'RELEASE_PROFILE_NOT_APPROVED'):
            builder.generate(self.repo)

    def test_palmistry_only_change_does_not_affect_bytes(self):
        before=builder.generate(self.repo)
        (self.repo/'PALMISTRY.md').write_text('# More palmistry research\n')
        git(self.repo, 'add', 'PALMISTRY.md')
        git(self.repo, 'commit', '-qm', 'unrelated palmistry')
        after=builder.generate(self.repo)
        # HEAD metadata changes by design, but canonical blob hashes & policy text do not.
        for name in ('source_manifest.json','source_integrity.json','policy_pack.json'):
            a=json.loads(before[name]);b=json.loads(after[name])
            a.pop('commit',None);b.pop('commit',None)
            a.pop('source_commit',None);b.pop('source_commit',None)
            self.assertEqual(a,b)
        self.assertEqual(before['canonical-repo/runtime/casting/core.py'],after['canonical-repo/runtime/casting/core.py'])

    def test_policy_digest_tampering_blocks_runtime(self):
        builder.sync(self.repo,check=False)
        with patch.object(policy_adapter, 'BASE',self.repo/'integrations/chatgpt-mcp'):
            policy_adapter._bundle.cache_clear()
            identity=policy_adapter.policy_identity()
            self.assertEqual(identity['policy_owner_count'],len(builder._ALLOWED_POLICY_FILES))
            context=policy_adapter.selected_policy('meihua')
            self.assertEqual(context['method'],'meihua')
            self.assertEqual(context['excerpts'][-1]['owner'],'MEIHUA.md')
            file=self.repo/'integrations/chatgpt-mcp/policy_pack.json'
            pack=json.loads(file.read_text(encoding='utf8'))
            pack['owners']['MEIHUA.md']['content']='tampered'
            file.write_text(json.dumps(pack),encoding='utf8')
            policy_adapter._bundle.cache_clear()
            with self.assertRaisesRegex(RuntimeError,'POLICY_DIGEST_MISMATCH'):
                policy_adapter.selected_policy('meihua')
        policy_adapter._bundle.cache_clear()

if __name__=='__main__':unittest.main()
